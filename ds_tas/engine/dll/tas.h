#pragma once
#include <Windows.h>

extern "C" __declspec(dllexport) void WaitHook();
extern "C" __declspec(dllexport) DWORD __stdcall GetInputStateHook(DWORD dwUserIndex, void *pState);
extern "C" __declspec(dllexport) BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved);
extern "C" __declspec(dllexport) DWORD __stdcall MouseInputHook(void *mInput);
extern "C" __declspec(dllexport) void __stdcall FrgpMouseHook(void *Mouse);
