#include <Windows.h>
#include <TlHelp32.h>
#include <tchar.h>
#include <stdexcept>
#include "tas.h"


DWORD_PTR hook::dwGetModuleBaseAddress(TCHAR *lpszModuleName)
	{
		HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, process_id);
		DWORD_PTR dwModuleBaseAddress = 0;
		if (hSnapshot != INVALID_HANDLE_VALUE)
		{
			MODULEENTRY32 ModuleEntry32 = { 0 };
			ModuleEntry32.dwSize = sizeof(MODULEENTRY32);
			if (Module32First(hSnapshot, &ModuleEntry32))
			{
				do
				{
					if (_tcscmp(ModuleEntry32.szModule, lpszModuleName) == 0)
					{
						dwModuleBaseAddress = (DWORD_PTR)ModuleEntry32.modBaseAddr;
						break;
					}
				} while (Module32Next(hSnapshot, &ModuleEntry32));
			}
			CloseHandle(hSnapshot);
		}
		return dwModuleBaseAddress;
	}
void hook::is_debug() {
	DWORD i;
	SIZE_T read;
	ReadProcessMemory(handle, (LPCVOID)0x400080, &i, 4, &read);
	if (i == 0xCE9634B4) {
		debug = true;
	}
	else {
		debug = false;
	}
}
hook::hook() {
		w_handle = FindWindow(NULL, "DARK SOULS");
		GetWindowThreadProcessId(w_handle, &process_id);
		xinput_address = dwGetModuleBaseAddress("XINPUT1_3.dll");
		handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, process_id);
		is_debug();
	};
void hook::read_input(INT16 out[20]) {
	//get the pointer
	BYTE *ptr = (BYTE*)xinput_address + 0x10C44;
	SIZE_T read;
	ReadProcessMemory(handle, ptr, &ptr, 4, &read);
	ReadProcessMemory(handle, ptr, &ptr, 4, &read);
	if (ptr == 0) {
		throw std::runtime_error("Couldn't find the pointer to the controller.");
	}
	ptr += 0x28;

	//read data
	BYTE data[12];
	ReadProcessMemory(handle, ptr, data, 12, &read);

	//load into INT16 array
	WORD bitmask[14] = { 0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0040,
	                       0x0080, 0x0100, 0x0200, 0x1000, 0x2000, 0x4000, 0x8000 };
	for (int i = 0; i < 14; i++) {
		out[i] = (bool)(*(WORD*)data & bitmask[i]);
	}
	out[14] = *(UINT8*)(data + 2);
	out[15] = *(UINT8*)(data + 3);
	out[16] = *(INT16*)(data + 4);
	out[17] = *(INT16*)(data + 6);
	out[18] = *(INT16*)(data + 8);
	out[19] = *(INT16*)(data + 10);
}
void hook::write_input(INT16* input) {
	//get the pointer
	BYTE *ptr = (BYTE*)xinput_address;
	ptr = ptr + 0x10C44;
	SIZE_T r;
	ReadProcessMemory(handle, ptr, &ptr, 4, &r);
	ReadProcessMemory(handle, ptr, &ptr, 4, &r);
	if (ptr == 0) {
		throw std::runtime_error("Couldn't find the pointer to the controller.");
	}
	ptr += 0x28;

	//cast data to the right type
	BYTE* data = new BYTE[12];
	WORD bitmask[14] = { 0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0040,
		                   0x0080, 0x0100, 0x0200, 0x1000, 0x2000, 0x4000, 0x8000 };
	for (int i = 0; i < 14; i++) {
		if (input[i]) {
			*(WORD*)data |= bitmask[i];
		}
		else {
			*(WORD*)data &= ~bitmask[i];
		}
	}
	*(UINT8*)(data + 2) = input[14];
	*(UINT8*)(data + 3) = input[15];
	*(INT16*)(data + 4) = input[16];
	*(INT16*)(data + 6) = input[17];
	*(INT16*)(data + 8) = input[18];
	*(INT16*)(data + 10) = input[19];

	//write data
	WriteProcessMemory(handle, ptr, data, 12, &r);
};
void hook::controller(bool state) {
	if (state) {
		//enable controller
		BYTE data[5] = { 0xe8, 0xa6, 0xfb, 0xff, 0xff };
		SIZE_T w;
		WriteProcessMemory(handle, (LPVOID)((BYTE*)xinput_address + 0x6945), data, 5, &w);
	}
	else {
		//disable controller
		BYTE data[5] = { 0x90, 0x90, 0x90, 0x90, 0x90 };
		SIZE_T w;
		WriteProcessMemory(handle, (LPVOID)((BYTE*)xinput_address + 0x6945), data, 5, &w);
	}
};
void hook::background_input(bool state) {
	BYTE *ptr;
	if (debug) {
		ptr = (BYTE*)0xF75BF3;
	}
	else {
		ptr = (BYTE*)0xF72543;
	}

	if (state) {
		BYTE data[3] = { 0xb0, 0x01, 0x90 };
		SIZE_T w;
		WriteProcessMemory(handle, ptr, data, 3, &w);
	}
	else {
		BYTE data[3] = { 0x0f, 0x94, 0xc0 };
		SIZE_T w;
		WriteProcessMemory(handle, ptr, data, 3, &w);
	}
};
UINT32 hook::igt() {
	BYTE *ptr;
	if (debug) {
		ptr = (BYTE*)0x137C8C0;
	}
	else {
		ptr = (BYTE*)0x1378700;
	}
	SIZE_T read;
	ReadProcessMemory(handle, ptr, &ptr, 4, &read);
	if (ptr == 0) {
		throw std::runtime_error("Couldn't find the pointer to IGT.");
	}
	ptr += 0x68;

	UINT32 out;
	ReadProcessMemory(handle, ptr, &out, 4, &read);
	return out;
}
UINT32 hook::frame_count() {
	BYTE *ptr;
	if (debug) {
		ptr = (BYTE*)0x137C7C4;
	}
	else {
		ptr = (BYTE*)0x1378604;
	}
	SIZE_T read;
	ReadProcessMemory(handle, ptr, &ptr, 4, &read);
	if (ptr == 0) {
		throw std::runtime_error("Could't find the pointer to the frame counter.");
	}
	ptr += 0x58;

	UINT32 out;
	ReadProcessMemory(handle, ptr, &out, 4, &read);
	return out;
}
HWND hook::get_w_handle() {
	return w_handle;
}


void* hook_new() {
	return new hook();
}
void hook_del(void* self) {
	delete (hook*)self;
}
void hook_read_input(void* self, INT16 out[20]) {
	return ((hook*)self)->read_input(out);
}
void hook_write_input(void* self, INT16 input[20]) {
	((hook*)self)->write_input(input);
}
void hook_controller(void* self, bool state) {
	((hook*)self)->controller(state);
}
void hook_background_input(void* self, bool state) {
	((hook*)self)->background_input(state);
}
UINT32 hook_igt(void* self) {
	return ((hook*)self)->igt();
}
UINT32 hook_frame_count(void* self) {
	return ((hook*)self)->frame_count();
}
void* hook_get_w_handle(void* self) {
	return ((hook*)self)->get_w_handle();
}
