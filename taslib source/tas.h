#pragma once
#include <Windows.h>



class hook {
private:
	HWND w_handle;
	HANDLE handle;
	DWORD process_id;
	DWORD_PTR xinput_address;
	bool debug;
	void is_debug();
	DWORD_PTR dwGetModuleBaseAddress(TCHAR *lpszModuleName);
public:
	hook();
	void read_input(INT16 out[20]);
	void write_input(INT16* input);
	void controller(bool state);
	void background_input(bool state);
	UINT32 igt();
	UINT32 frame_count();
	HWND get_w_handle();
};


#define DllExport __declspec(dllexport)

extern "C"{
	DllExport void* hook_new();
	DllExport void hook_del(void* self);
	DllExport void hook_read_input(void* self, INT16 out[20]);
	DllExport void hook_write_input(void* self, INT16 input[20]);
	DllExport void hook_controller(void* self, bool state);
	DllExport void hook_background_input(void* self, bool state);
	DllExport UINT32 hook_igt(void* self);
	DllExport UINT32 hook_frame_count(void* self);
	DllExport void* hook_get_w_handle(void* self);
}
