"""
"""
import ctypes


class BaseLoc:
    """Base class for pointers to in game data
    """
    def __init__(
        self, offsets, read_memory=None, write_memory=None, parent=None
    ):
        """read_fn(address, len) -> bytes
        write_fn(address, bytes)
        """
        if parent is not None:
            self.read_memory = parent.read_memory
            self.write_memory = parent.write_memory
        else:
            self.read_memory = read_memory
            self.write_memory = write_memory

        if not isinstance(offsets, (list, tuple)):
            offsets = [offsets]
        if len(offsets) == 1:
            self.offset = offsets[0]
            self.parent = parent
        else:
            self.offset = offsets[-1]
            self.parent = MemLoc(ctypes.wintypes.DWORD)(
                offsets[:-1], read_memory, write_memory, parent
            )

    @property
    def offsets(self):
        if self.parent is not None:
            return self.parent.offsets + [hex(self.offset)]
        return [hex(self.offset)]

    @property
    def address(self):
        if self.parent is not None:
            ptr = self.parent.value
            if ptr == 0:
                raise RuntimeError(f"Null pointer {self.parent}")
        else:
            ptr = 0
        ptr += self.offset
        return ptr

    @property
    def value(self):
        buffer = self.read_memory(self.address, ctypes.sizeof(self.type))
        return self.type.from_buffer_copy(buffer)

    @value.setter
    def value(self, value):
        if not isinstance(value, self.type):
            value = self.type(value)
        data = bytes(value)
        self.write_memory(self.address, data)


class SimpleDataLoc(BaseLoc):
    @property
    def value(self):
        buffer = self.read_memory(self.address, ctypes.sizeof(self.type))
        return self.type.from_buffer_copy(buffer).value

    @value.setter
    def value(self, value):
        if not isinstance(value, self.type):
            value = self.type(value)
        data = bytes(value)
        self.write_memory(self.address, data)


# Restructure


class StructLoc(SimpleDataLoc):
    def __getattr__(self, name):
        ofs = getattr(self.type, name).offset

        t = None
        for field in self.type._fields_:
            if name == field[0]:
                t = field[1]
                break
        if t is None:
            raise AttributeError  # TODO

        return MemLoc(t)(
            self.offset+ofs,
            self.read_memory,
            self.write_memory,
            self.parent
        )


Structure = ctypes.Structure


class AnonStructure:
    def __new__(cls, *fields):
        name = 'Struct' + str(id(cls))

        obj = type(
            name,
            (ctypes.Structure,),
            {"_fields_": fields}
        )
        return obj


# Partial Structures


class PartStructLoc(BaseLoc):
    def __getattr__(self, name):
        offset, type_ = self.type.fields[name]
        return MemLoc(type_)(
            self.offset+offset,
            self.read_memory,
            self.write_memory,
            self.parent
        )


class PartStructType(type):
    def __init__(self, name, bases, namespace):
        self.__name__ = name
        self.fields = {}
        if '_fields_' in namespace:
            for name, ofs, t in namespace['_fields_']:
                self.fields[name] = (ofs, t)


class PartStruct(metaclass=PartStructType):
    pass


class AnonPartStruct(PartStructType):
    def __new__(cls, *fields):
        name = 'PartStruct' + str(id(cls))

        obj = type(
            name,
            (PartStruct,),
            {'_fields_': fields}
        )
        return obj


# Pointers


class PointerLoc(SimpleDataLoc):
    def __init_subclass__(cls):
        cls._content = cls.type.type

    @property
    def content(self):
        return MemLoc(self._content)(0, self.read_memory, self.write_memory, self)


class Pointer32(ctypes.Structure):
    pass


class POINTER32(type(ctypes.Structure)):
    """Analog to ctypes.POINTER but for 32 bit pointers
    To be used to pass pointers to MemLoc
    """
    _instances = {}

    def __new__(cls, type_):
        if type_ in cls._instances:
            return cls._instances[type_]

        name = "LP32_" + type_.__name__

        obj = type(
            name,
            (Pointer32,),
            {"type": type_, "_fields_": [("value", ctypes.c_uint32)]}
        )
        return obj


class LPVOID32(ctypes.c_uint32):
    pass


# Arrays


class ArrayLoc(BaseLoc):
    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= self.type._length_:
                raise IndexError
            return MemLoc(self.type._type_)(
                self.offset+key*ctypes.sizeof(self.type._type_),
                self.read_memory,
                self.write_memory,
                self.parent
            )
        else:
            raise ValueError


# Queues


class QueueLoc(PartStructLoc):
    def __getitem__(self, key):
        if isinstance(key, int):
            start = self.start.value
            end = self.end.value
            size = self.size.value
            if key >= (end-start) % size:
                raise IndexError

            index = (start + key) % size
            return self.array[index]
        else:
            raise ValueError


class Queue(PartStruct):
    pass


class MemLoc(type):
    """Metaclass for in game memory locations

    Examples:
        Creating memory location for uint32 stored at [[0x123456]+0xC]+0x4:
            MemLoc(ctypes.c_uint32)([0x123456, 0xC, 0x4])

        Creating memory location for a structure at 0xFEDCBA:
            MyStruct(ctypes.Structure):
                _fields_ = [('Int', ctypes.c_int), ...]
            struct_mem_loc = MemLoc(MyStruct)(0xFEDCBA)
        You can then access MemLocs for fields like:
            struct_mem_loc.Int
    """
    _instances = {}

    def __new__(cls, type_):
        if type_ in cls._instances:
            return cls._instances[type_]

        name = "MemLoc_" + type_.__name__

        if issubclass(type_, Pointer32):
            bases = (PointerLoc,)
        elif issubclass(type_, Queue):
            bases = (QueueLoc,)
        elif issubclass(type_, Structure):
            bases = (StructLoc,)
        elif issubclass(type_, PartStruct):
            bases = (PartStructLoc,)
        elif isinstance(type_, type(ctypes.c_char)):
            bases = (SimpleDataLoc,)
        elif isinstance(type_, type(ctypes.c_char*1)):
            bases = (ArrayLoc,)
        else:
            bases = (BaseLoc,)

        obj = super().__new__(cls, name, bases, {"type": type_})
        cls._instances[type_] = obj
        return obj


class Patch():
    def __init__(self, address, original, patch=None):
        self.address = address
        self.orig = original
        self.patch = patch
