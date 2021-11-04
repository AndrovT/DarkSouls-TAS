#include <Windows.h>
#include <stdio.h> 

struct XINPUT_GAMEPAD {
  WORD  wButtons;
  BYTE  bLeftTrigger;
  BYTE  bRightTrigger;
  SHORT sThumbLX;
  SHORT sThumbLY;
  SHORT sThumbRX;
  SHORT sThumbRY;
};

struct XINPUT_STATE {
  DWORD          dwPacketNumber;
  XINPUT_GAMEPAD Gamepad;
};

struct MOUSE_INPUT {
    int XMovment;
    int YMovment;
    int Scroll;
    BYTE Mouse1;
    BYTE Mouse2;
    BYTE Mouse3;
    BYTE Mouse4;
    BYTE Mouse5;
};

struct CLICK {
    bool Down;
    bool Up;
    bool Hold;
    BYTE Empty;
    float HoldTime;
};

struct FRGP_MOUSE {
    DWORD Unk1;
    DWORD Unk2;
    CLICK Left;
    CLICK Right;
    CLICK Middle;
    int X;
    int Y;
    int PrevX;
    int PrevY;
    int Scroll;
    int PrevScroll;
    int Change;
};

struct INPUT_STATE {
    XINPUT_GAMEPAD Gamepad;
    MOUSE_INPUT Mouse;
};

struct SharedData {
    BYTE Mode;
    BYTE WaitFlag;
    bool Sync;
    float FrameTime;
    DWORD FrameCount; 
    INPUT_STATE InputState;
    LPVOID WaitHook;
    LPVOID GetInputStateHook;
    LPVOID MouseInputHook;
    LPVOID FrgpMouseHook;
    LPVOID QPCHook;
} ShrData;

const float FRAME_TIME = 0.03333333507F;

LARGE_INTEGER Frequency, LastTime, Time;

DWORD PacketNum;


void WaitHook(){
    if(ShrData.FrameTime>0) {
        while(Time.LowPart-LastTime.LowPart<ShrData.FrameTime*Frequency.QuadPart) {
            QueryPerformanceCounter(&Time);
        }
        LastTime = Time;
    }
    if(ShrData.Mode == 2) {
        ShrData.WaitFlag = 2;
        while (ShrData.WaitFlag != 1) {
            Sleep(1);
        }
    }
}


DWORD __stdcall GetInputStateHook(DWORD dwUserIndex, XINPUT_STATE *pState) {
    if(ShrData.Mode == 1) {
        while(ShrData.Sync) {
            Sleep(1);
        }
    }
    PacketNum++;
    pState->dwPacketNumber = PacketNum;
    pState->Gamepad = ShrData.InputState.Gamepad;

    return ERROR_SUCCESS;
}


DWORD __stdcall MouseInputHook(MOUSE_INPUT *mInput) {
    if(ShrData.Mode == 1) {
        while(ShrData.Sync) {
            Sleep(1);
        }
    }

    *mInput = ShrData.InputState.Mouse;
    return 0;
}


void ClickUpdate(CLICK *Click, BYTE State){
    if(State){
        if(Click->Hold) {
            Click->Down = false;
            Click->HoldTime += FRAME_TIME;
        } else {
            Click->Down = true;
            Click->Up = false;
            Click->Hold = true;
        }
    } else {
        if(Click->Hold) {
            Click->Up = true;
            Click->Down = false;
            Click->Hold = false;
            Click->HoldTime = 0;
        } else {
            Click->Up = false;
        }
    }    
}


void __stdcall FrgpMouseHook(FRGP_MOUSE *Mouse) {
    if(ShrData.Mode == 1) {
        while(ShrData.Sync) {
            Sleep(1);
        }
    }

    ClickUpdate(&(Mouse->Left), ShrData.InputState.Mouse.Mouse1);
    ClickUpdate(&(Mouse->Right), ShrData.InputState.Mouse.Mouse2);
    ClickUpdate(&(Mouse->Middle), ShrData.InputState.Mouse.Mouse2);

    Mouse->PrevX = Mouse->X;
    Mouse->PrevY = Mouse->Y;

    Mouse->X += ShrData.InputState.Mouse.XMovment;
    Mouse->Y += ShrData.InputState.Mouse.YMovment;

    if(Mouse->X>1280) {
        Mouse->X = 1280;
    } else if(Mouse->X<0) {
        Mouse->X = 0;
    }
    if(Mouse->Y>720) {
        Mouse->Y = 720;
    } else if(Mouse->Y<0) {
        Mouse->Y = 0;
    }

    //TODO: Check if this is correct
    //Eh
    Mouse->PrevScroll = Mouse->Scroll;
    Mouse->Scroll = ShrData.InputState.Mouse.Scroll;

    if(Mouse->X==Mouse->PrevX && Mouse->Y==Mouse->PrevY){
        Mouse->Change = 0;
    } else {
        Mouse->Change = 1;
    }

    ShrData.Sync = true;
}


BOOL __stdcall QPCHook(LARGE_INTEGER *lpPerformanceCount) {
    lpPerformanceCount->QuadPart = (long long)ShrData.FrameCount*Frequency.QuadPart*FRAME_TIME;
    return 1;
}


BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,
    DWORD fdwReason,
    LPVOID lpReserved )
{
    switch(fdwReason) 
    {
        case DLL_PROCESS_ATTACH:
            ShrData.Mode = 0;
            ShrData.WaitFlag = 0;
            ShrData.FrameTime = FRAME_TIME;
            ShrData.WaitHook = (LPVOID)&WaitHook;
            ShrData.GetInputStateHook = (LPVOID)&GetInputStateHook;
            ShrData.MouseInputHook = (LPVOID)&MouseInputHook;
            ShrData.FrgpMouseHook = (LPVOID)&FrgpMouseHook;
            ShrData.QPCHook = (LPVOID)&QPCHook;
            QueryPerformanceFrequency(&Frequency);
            break;

        case DLL_THREAD_ATTACH:
         // Do thread-specific initialization.
            break;

        case DLL_THREAD_DETACH:
         // Do thread-specific cleanup.
            break;

        case DLL_PROCESS_DETACH:
         // Perform any necessary cleanup.
            break;
    }
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}