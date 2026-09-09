/**
 * ============================================================================
 * PC PERFORMANCE BENCHMARK & BOTTLENECK ANALYSIS SUITE
 * PHASE 0 — ENVIRONMENT AUDIT & HARDWARE DIAGNOSTIC
 * ============================================================================
 * 
 * Target Platform: Windows 10/11 x64
 * Primary Hardware: Intel Core i5-11400H + NVIDIA GeForce GTX 1650 Laptop GPU
 * Language: C++20 (MSVC)
 * Dependencies: Pure Win32 APIs, CPUID intrinsics, WMI (COM), dynamic NVML/CUDA.
 * 
 * Output: Terminal Report + results/system_info.json
 * ============================================================================
 */

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include <cstring>
#include <cstdint>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <intrin.h>
#include <wbemidl.h>
#include <comdef.h>

#pragma comment(lib, "wbemuuid.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")
#pragma comment(lib, "Advapi32.lib")

// ============================================================================
// DATA STRUCTURES FOR SYSTEM TELEMETRY
// ============================================================================

struct CacheInfo {
    int level = 0;
    std::string type;
    uint64_t sizeKB = 0;
    int associativity = 0;
    int lineSize = 0;
};

struct CpuAudit {
    std::string modelName;
    std::string vendor;
    int physicalCores = 0;
    int logicalProcessors = 0;
    int baseFrequencyMHz = 0;
    int maxFrequencyMHz = 0;
    int busFrequencyMHz = 0;
    std::map<std::string, bool> instructions;
    std::vector<CacheInfo> caches;
};

struct RamModule {
    std::string locator;
    uint64_t capacityGB = 0;
    uint32_t configuredSpeedMTs = 0;
    std::string manufacturer;
    std::string partNumber;
};

struct RamAudit {
    uint64_t totalPhysicalMB = 0;
    uint64_t availablePhysicalMB = 0;
    uint32_t memoryLoadPercent = 0;
    std::vector<RamModule> modules;
    std::string channelConfiguration;
};

struct GpuAudit {
    bool detected = false;
    std::string name;
    std::string driverVersion;
    int cudaDriverVersionRaw = 0;
    std::string cudaDriverVersionStr;
    int computeMajor = 0;
    int computeMinor = 0;
    int smCount = 0;
    int warpSize = 32;
    int maxThreadsPerBlock = 0;
    int sharedMemPerBlockKB = 0;
    int memoryBusWidthBits = 0;
    int l2CacheKB = 0;
    uint64_t vramTotalMB = 0;
    uint64_t vramFreeMB = 0;
    uint64_t vramUsedMB = 0;
    uint32_t coreClockMHz = 0;
    uint32_t memoryClockMHz = 0;
    uint32_t temperatureC = 0;
    float powerUsageWatts = 0.0f;
    float powerLimitWatts = 0.0f;
};

struct OsAudit {
    std::string osName = "Windows";
    std::string versionString;
    uint32_t buildNumber = 0;
    std::string architecture;
    std::string compilerVersion;
    std::string cppStandard;
};

struct SystemInfo {
    OsAudit os;
    CpuAudit cpu;
    RamAudit ram;
    GpuAudit gpu;
};

// ============================================================================
// CPU DETECTION HELPERS
// ============================================================================

static void AuditCpuFeatures(CpuAudit& cpu) {
    int info[4] = {0, 0, 0, 0};

    // Brand / Model Name (Extended Leaves 0x80000002 to 0x80000004)
    __cpuid(info, 0x80000000);
    unsigned int nExIds = info[0];
    char brand[49] = {0};

    if (nExIds >= 0x80000004) {
        __cpuid((int*)(brand + 0),  0x80000002);
        __cpuid((int*)(brand + 16), 0x80000003);
        __cpuid((int*)(brand + 32), 0x80000004);
        brand[48] = '\0';
        // Trim leading spaces
        char* p = brand;
        while (*p == ' ') p++;
        cpu.modelName = p;
    } else {
        cpu.modelName = "Unknown x86_64 CPU";
    }

    // Vendor string
    __cpuid(info, 0);
    char vendor[13] = {0};
    *reinterpret_cast<int*>(vendor + 0) = info[1]; // EBX
    *reinterpret_cast<int*>(vendor + 4) = info[3]; // EDX
    *reinterpret_cast<int*>(vendor + 8) = info[2]; // ECX
    vendor[12] = '\0';
    cpu.vendor = vendor;

    // Feature Flags Leaf 1
    __cpuid(info, 1);
    int ecx1 = info[2];
    int edx1 = info[3];

    cpu.instructions["MMX"]     = (edx1 & (1 << 23)) != 0;
    cpu.instructions["SSE"]     = (edx1 & (1 << 25)) != 0;
    cpu.instructions["SSE2"]    = (edx1 & (1 << 26)) != 0;
    cpu.instructions["SSE3"]    = (ecx1 & (1 << 0))  != 0;
    cpu.instructions["SSSE3"]   = (ecx1 & (1 << 9))  != 0;
    cpu.instructions["SSE4.1"]  = (ecx1 & (1 << 19)) != 0;
    cpu.instructions["SSE4.2"]  = (ecx1 & (1 << 20)) != 0;
    cpu.instructions["AES-NI"]  = (ecx1 & (1 << 25)) != 0;
    cpu.instructions["FMA3"]    = (ecx1 & (1 << 12)) != 0;
    cpu.instructions["AVX"]     = (ecx1 & (1 << 28)) != 0;

    // Check OSXSAVE support before querying extended register states
    bool osxsave = (ecx1 & (1 << 27)) != 0;
    cpu.instructions["OSXSAVE"] = osxsave;

    // Feature Flags Leaf 7 Subleaf 0
    __cpuidex(info, 7, 0);
    int ebx7 = info[1];
    int ecx7 = info[2];
    int edx7 = info[3];

    cpu.instructions["AVX2"]        = (ebx7 & (1 << 5))  != 0;
    cpu.instructions["BMI1"]        = (ebx7 & (1 << 3))  != 0;
    cpu.instructions["BMI2"]        = (ebx7 & (1 << 8))  != 0;
    cpu.instructions["AVX-512F"]    = (ebx7 & (1 << 16)) != 0;
    cpu.instructions["AVX-512DQ"]   = (ebx7 & (1 << 17)) != 0;
    cpu.instructions["AVX-512CD"]   = (ebx7 & (1 << 28)) != 0;
    cpu.instructions["AVX-512BW"]   = (ebx7 & (1 << 30)) != 0;
    cpu.instructions["AVX-512VL"]   = (ebx7 & (1 << 31)) != 0;
    cpu.instructions["AVX-512VNNI"] = (ecx7 & (1 << 11)) != 0;

    // Verify OS state saving for AVX / AVX-512 via XCR0
    if (osxsave) {
        unsigned __int64 xcr0 = _xgetbv(0);
        bool ymmEnabled = (xcr0 & 0x6) == 0x6; // XMM (bit 1) and YMM (bit 2)
        bool zmmEnabled = (xcr0 & 0xE6) == 0xE6; // OPMASK, ZMM_Hi256, Hi16_ZMM
        cpu.instructions["OS_AVX_Enabled"] = ymmEnabled;
        cpu.instructions["OS_AVX512_Enabled"] = zmmEnabled;
    } else {
        cpu.instructions["OS_AVX_Enabled"] = false;
        cpu.instructions["OS_AVX512_Enabled"] = false;
    }

    // Frequencies via CPUID Leaf 0x16 (Intel Skylake+)
    __cpuid(info, 0);
    if (info[0] >= 0x16) {
        __cpuid(info, 0x16);
        cpu.baseFrequencyMHz = info[0]; // EAX
        cpu.maxFrequencyMHz  = info[1]; // EBX
        cpu.busFrequencyMHz  = info[2]; // ECX
    }
}

static void AuditCpuTopologyAndCaches(CpuAudit& cpu) {
    DWORD returnLength = 0;
    GetLogicalProcessorInformationEx(RelationAll, nullptr, &returnLength);

    if (GetLastError() != ERROR_INSUFFICIENT_BUFFER || returnLength == 0) {
        return;
    }

    std::vector<uint8_t> buffer(returnLength);
    PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX pInfo = 
        reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(buffer.data());

    if (!GetLogicalProcessorInformationEx(RelationAll, pInfo, &returnLength)) {
        return;
    }

    int physicalCores = 0;
    int logicalProcessors = 0;
    std::vector<CacheInfo> caches;

    uint8_t* ptr = buffer.data();
    uint8_t* end = buffer.data() + returnLength;

    while (ptr < end) {
        pInfo = reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(ptr);

        if (pInfo->Relationship == RelationProcessorCore) {
            physicalCores++;
            // Count logical processors in this core mask
            for (WORD group = 0; group < pInfo->Processor.GroupCount; ++group) {
                KAFFINITY mask = pInfo->Processor.GroupMask[group].Mask;
                while (mask) {
                    if (mask & 1) logicalProcessors++;
                    mask >>= 1;
                }
            }
        } else if (pInfo->Relationship == RelationCache) {
            CacheInfo c;
            c.level = pInfo->Cache.Level;
            c.associativity = pInfo->Cache.Associativity;
            c.lineSize = pInfo->Cache.LineSize;
            c.sizeKB = pInfo->Cache.CacheSize / 1024;

            switch (pInfo->Cache.Type) {
                case CacheUnified:     c.type = "Unified"; break;
                case CacheInstruction: c.type = "Instruction"; break;
                case CacheData:        c.type = "Data"; break;
                case CacheTrace:       c.type = "Trace"; break;
                default:               c.type = "Unknown"; break;
            }
            caches.push_back(c);
        }

        ptr += pInfo->Size;
    }

    cpu.physicalCores = physicalCores;
    cpu.logicalProcessors = logicalProcessors;
    cpu.caches = caches;
}

// ============================================================================
// RAM DETECTION (WIN32 + WMI)
// ============================================================================

static void AuditRam(RamAudit& ram) {
    // 1. Basic OS Memory Status
    MEMORYSTATUSEX memStatus;
    memStatus.dwLength = sizeof(memStatus);
    if (GlobalMemoryStatusEx(&memStatus)) {
        ram.totalPhysicalMB = memStatus.ullTotalPhys / (1024 * 1024);
        ram.availablePhysicalMB = memStatus.ullAvailPhys / (1024 * 1024);
        ram.memoryLoadPercent = memStatus.dwMemoryLoad;
    }

    // 2. Query Physical Modules via WMI
    HRESULT hres = CoInitializeEx(0, COINIT_MULTITHREADED);
    bool coInitialized = SUCCEEDED(hres);

    IWbemLocator* pLoc = nullptr;
    hres = CoCreateInstance(CLSID_WbemLocator, 0, CLSCTX_INPROC_SERVER,
                            IID_IWbemLocator, (LPVOID*)&pLoc);

    if (SUCCEEDED(hres) && pLoc) {
        IWbemServices* pSvc = nullptr;
        hres = pLoc->ConnectServer(_bstr_t(L"ROOT\\CIMV2"), nullptr, nullptr, 0,
                                   0, 0, 0, &pSvc);

        if (SUCCEEDED(hres) && pSvc) {
            hres = CoSetProxyBlanket(pSvc, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE,
                                     nullptr, RPC_C_AUTHN_LEVEL_CALL,
                                     RPC_C_IMP_LEVEL_IMPERSONATE, nullptr, EOAC_NONE);

            IEnumWbemClassObject* pEnumerator = nullptr;
            hres = pSvc->ExecQuery(
                bstr_t("WQL"),
                bstr_t("SELECT DeviceLocator, Capacity, Speed, ConfiguredClockSpeed, Manufacturer, PartNumber FROM Win32_PhysicalMemory"),
                WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY, nullptr, &pEnumerator);

            if (SUCCEEDED(hres) && pEnumerator) {
                IWbemClassObject* pclsObj = nullptr;
                ULONG uReturn = 0;

                while (pEnumerator) {
                    hres = pEnumerator->Next(WBEM_INFINITE, 1, &pclsObj, &uReturn);
                    if (uReturn == 0) break;

                    RamModule mod;
                    VARIANT vtProp;

                    // Device Locator
                    hres = pclsObj->Get(L"DeviceLocator", 0, &vtProp, 0, 0);
                    if (SUCCEEDED(hres) && vtProp.vt == VT_BSTR) {
                        mod.locator = _bstr_t(vtProp.bstrVal);
                        VariantClear(&vtProp);
                    }

                    // Capacity
                    hres = pclsObj->Get(L"Capacity", 0, &vtProp, 0, 0);
                    if (SUCCEEDED(hres) && vtProp.vt == VT_BSTR) {
                        uint64_t bytes = _wtoi64(vtProp.bstrVal);
                        mod.capacityGB = bytes / (1024ULL * 1024ULL * 1024ULL);
                        VariantClear(&vtProp);
                    }

                    // ConfiguredClockSpeed or Speed
                    hres = pclsObj->Get(L"ConfiguredClockSpeed", 0, &vtProp, 0, 0);
                    if (SUCCEEDED(hres) && (vtProp.vt == VT_I4 || vtProp.vt == VT_UI4)) {
                        mod.configuredSpeedMTs = vtProp.uintVal;
                        VariantClear(&vtProp);
                    } else {
                        hres = pclsObj->Get(L"Speed", 0, &vtProp, 0, 0);
                        if (SUCCEEDED(hres) && (vtProp.vt == VT_I4 || vtProp.vt == VT_UI4)) {
                            mod.configuredSpeedMTs = vtProp.uintVal;
                            VariantClear(&vtProp);
                        }
                    }

                    // Manufacturer
                    hres = pclsObj->Get(L"Manufacturer", 0, &vtProp, 0, 0);
                    if (SUCCEEDED(hres) && vtProp.vt == VT_BSTR) {
                        mod.manufacturer = _bstr_t(vtProp.bstrVal);
                        VariantClear(&vtProp);
                    }

                    // Part Number
                    hres = pclsObj->Get(L"PartNumber", 0, &vtProp, 0, 0);
                    if (SUCCEEDED(hres) && vtProp.vt == VT_BSTR) {
                        mod.partNumber = _bstr_t(vtProp.bstrVal);
                        VariantClear(&vtProp);
                    }

                    ram.modules.push_back(mod);
                    pclsObj->Release();
                }
                pEnumerator->Release();
            }
            pSvc->Release();
        }
        pLoc->Release();
    }
    if (coInitialized) {
        CoUninitialize();
    }

    // Determine Channel Configuration
    if (ram.modules.size() >= 2) {
        ram.channelConfiguration = "Dual Channel (Populated in " + std::to_string(ram.modules.size()) + " slots)";
    } else if (ram.modules.size() == 1) {
        ram.channelConfiguration = "Single Channel (1 DIMM populated — Potential Memory Bandwidth Bottleneck)";
    } else {
        ram.channelConfiguration = "Undetectable via WMI";
    }
}

// ============================================================================
// GPU AUDIT (DYNAMIC NVML & CUDA DRIVER API)
// ============================================================================

// NVML Function Pointer Signatures
typedef int nvmlReturn_t;
typedef void* nvmlDevice_t;
typedef struct {
    unsigned long long total;
    unsigned long long free;
    unsigned long long used;
} nvmlMemory_t;

typedef nvmlReturn_t (*pfn_nvmlInit_v2)();
typedef nvmlReturn_t (*pfn_nvmlShutdown)();
typedef nvmlReturn_t (*pfn_nvmlDeviceGetHandleByIndex_v2)(unsigned int, nvmlDevice_t*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetName)(nvmlDevice_t, char*, unsigned int);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetMemoryInfo)(nvmlDevice_t, nvmlMemory_t*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetClockInfo)(nvmlDevice_t, int, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetTemperature)(nvmlDevice_t, int, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetPowerUsage)(nvmlDevice_t, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlDeviceGetEnforcedPowerLimit)(nvmlDevice_t, unsigned int*);
typedef nvmlReturn_t (*pfn_nvmlSystemGetDriverVersion)(char*, unsigned int);

// CUDA Driver API Function Pointer Signatures
typedef int CUresult;
typedef int CUdevice;
typedef unsigned __int64 cuuint64_t;

typedef CUresult (*pfn_cuInit)(unsigned int);
typedef CUresult (*pfn_cuDriverGetVersion)(int*);
typedef CUresult (*pfn_cuDeviceGetCount)(int*);
typedef CUresult (*pfn_cuDeviceGet)(CUdevice*, int);
typedef CUresult (*pfn_cuDeviceGetName)(char*, int, CUdevice);
typedef CUresult (*pfn_cuDeviceComputeCapability)(int*, int*, CUdevice);
typedef CUresult (*pfn_cuDeviceGetAttribute)(int*, int, CUdevice);
typedef CUresult (*pfn_cuDeviceTotalMem)(cuuint64_t*, CUdevice);

#define CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT 16
#define CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK 1
#define CU_DEVICE_ATTRIBUTE_WARP_SIZE 10
#define CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK 8
#define CU_DEVICE_ATTRIBUTE_GLOBAL_MEMORY_BUS_WIDTH 58
#define CU_DEVICE_ATTRIBUTE_L2_CACHE_SIZE 37

static void AuditGpu(GpuAudit& gpu) {
    // 1. Try NVML first for live sensor readings, driver version, clocks, and power
    HMODULE hNvml = LoadLibraryA("nvml.dll");
    if (hNvml) {
        auto fn_init = (pfn_nvmlInit_v2)GetProcAddress(hNvml, "nvmlInit_v2");
        auto fn_shutdown = (pfn_nvmlShutdown)GetProcAddress(hNvml, "nvmlShutdown");
        auto fn_getHandle = (pfn_nvmlDeviceGetHandleByIndex_v2)GetProcAddress(hNvml, "nvmlDeviceGetHandleByIndex_v2");
        auto fn_getName = (pfn_nvmlDeviceGetName)GetProcAddress(hNvml, "nvmlDeviceGetName");
        auto fn_getMem = (pfn_nvmlDeviceGetMemoryInfo)GetProcAddress(hNvml, "nvmlDeviceGetMemoryInfo");
        auto fn_getClock = (pfn_nvmlDeviceGetClockInfo)GetProcAddress(hNvml, "nvmlDeviceGetClockInfo");
        auto fn_getTemp = (pfn_nvmlDeviceGetTemperature)GetProcAddress(hNvml, "nvmlDeviceGetTemperature");
        auto fn_getPower = (pfn_nvmlDeviceGetPowerUsage)GetProcAddress(hNvml, "nvmlDeviceGetPowerUsage");
        auto fn_getPowerLimit = (pfn_nvmlDeviceGetEnforcedPowerLimit)GetProcAddress(hNvml, "nvmlDeviceGetEnforcedPowerLimit");
        auto fn_getDriver = (pfn_nvmlSystemGetDriverVersion)GetProcAddress(hNvml, "nvmlSystemGetDriverVersion");

        if (fn_init && fn_init() == 0) {
            gpu.detected = true;
            char driverVer[64] = {0};
            if (fn_getDriver && fn_getDriver(driverVer, sizeof(driverVer)) == 0) {
                gpu.driverVersion = driverVer;
            }

            nvmlDevice_t dev = nullptr;
            if (fn_getHandle && fn_getHandle(0, &dev) == 0) {
                char devName[96] = {0};
                if (fn_getName && fn_getName(dev, devName, sizeof(devName)) == 0) {
                    gpu.name = devName;
                }

                nvmlMemory_t mem;
                if (fn_getMem && fn_getMem(dev, &mem) == 0) {
                    gpu.vramTotalMB = mem.total / (1024 * 1024);
                    gpu.vramFreeMB  = mem.free  / (1024 * 1024);
                    gpu.vramUsedMB  = mem.used  / (1024 * 1024);
                }

                unsigned int coreClock = 0;
                if (fn_getClock && fn_getClock(dev, 0 /* Graphics */, &coreClock) == 0) {
                    gpu.coreClockMHz = coreClock;
                }

                unsigned int memClock = 0;
                if (fn_getClock && fn_getClock(dev, 2 /* Memory */, &memClock) == 0) {
                    gpu.memoryClockMHz = memClock;
                }

                unsigned int temp = 0;
                if (fn_getTemp && fn_getTemp(dev, 0 /* GPU temp */, &temp) == 0) {
                    gpu.temperatureC = temp;
                }

                unsigned int pwr = 0;
                if (fn_getPower && fn_getPower(dev, &pwr) == 0) {
                    gpu.powerUsageWatts = pwr / 1000.0f;
                }

                unsigned int pwrLimit = 0;
                if (fn_getPowerLimit && fn_getPowerLimit(dev, &pwrLimit) == 0) {
                    gpu.powerLimitWatts = pwrLimit / 1000.0f;
                }
            }
            if (fn_shutdown) fn_shutdown();
        }
        FreeLibrary(hNvml);
    }

    // 2. Interrogate CUDA Driver API (nvcuda.dll) for Compute Architecture details
    HMODULE hCuda = LoadLibraryA("nvcuda.dll");
    if (hCuda) {
        auto fn_cuInit = (pfn_cuInit)GetProcAddress(hCuda, "cuInit");
        auto fn_cuDriverVer = (pfn_cuDriverGetVersion)GetProcAddress(hCuda, "cuDriverGetVersion");
        auto fn_cuDevGet = (pfn_cuDeviceGet)GetProcAddress(hCuda, "cuDeviceGet");
        auto fn_cuDevName = (pfn_cuDeviceGetName)GetProcAddress(hCuda, "cuDeviceGetName");
        auto fn_cuComputeCap = (pfn_cuDeviceComputeCapability)GetProcAddress(hCuda, "cuDeviceComputeCapability");
        auto fn_cuDevAttr = (pfn_cuDeviceGetAttribute)GetProcAddress(hCuda, "cuDeviceGetAttribute");

        if (fn_cuInit && fn_cuInit(0) == 0) {
            gpu.detected = true;
            int driverVer = 0;
            if (fn_cuDriverVer && fn_cuDriverVer(&driverVer) == 0) {
                gpu.cudaDriverVersionRaw = driverVer;
                int major = driverVer / 1000;
                int minor = (driverVer % 1000) / 10;
                gpu.cudaDriverVersionStr = std::to_string(major) + "." + std::to_string(minor);
            }

            CUdevice dev = 0;
            if (fn_cuDevGet && fn_cuDevGet(&dev, 0) == 0) {
                if (gpu.name.empty() && fn_cuDevName) {
                    char nameBuf[96] = {0};
                    if (fn_cuDevName(nameBuf, sizeof(nameBuf), dev) == 0) {
                        gpu.name = nameBuf;
                    }
                }

                int major = 0, minor = 0;
                if (fn_cuComputeCap && fn_cuComputeCap(&major, &minor, dev) == 0) {
                    gpu.computeMajor = major;
                    gpu.computeMinor = minor;
                }

                int smCount = 0;
                if (fn_cuDevAttr && fn_cuDevAttr(&smCount, CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT, dev) == 0) {
                    gpu.smCount = smCount;
                }

                int maxThreads = 0;
                if (fn_cuDevAttr && fn_cuDevAttr(&maxThreads, CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK, dev) == 0) {
                    gpu.maxThreadsPerBlock = maxThreads;
                }

                int warpSize = 32;
                if (fn_cuDevAttr && fn_cuDevAttr(&warpSize, CU_DEVICE_ATTRIBUTE_WARP_SIZE, dev) == 0) {
                    gpu.warpSize = warpSize;
                }

                int sharedMem = 0;
                if (fn_cuDevAttr && fn_cuDevAttr(&sharedMem, CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK, dev) == 0) {
                    gpu.sharedMemPerBlockKB = sharedMem / 1024;
                }

                int busWidth = 0;
                if (fn_cuDevAttr && fn_cuDevAttr(&busWidth, CU_DEVICE_ATTRIBUTE_GLOBAL_MEMORY_BUS_WIDTH, dev) == 0) {
                    gpu.memoryBusWidthBits = busWidth;
                }

                int l2Size = 0;
                if (fn_cuDevAttr && fn_cuDevAttr(&l2Size, CU_DEVICE_ATTRIBUTE_L2_CACHE_SIZE, dev) == 0) {
                    gpu.l2CacheKB = l2Size / 1024;
                }
            }
        }
        FreeLibrary(hCuda);
    }
}

// ============================================================================
// OS & ENVIRONMENT DETECTION
// ============================================================================

typedef LONG(NTAPI* pfn_RtlGetVersion)(PRTL_OSVERSIONINFOW);

static void AuditOs(OsAudit& os) {
    // Exact Windows Build using RtlGetVersion from ntdll
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    if (hNtdll) {
        auto fn_RtlGetVersion = (pfn_RtlGetVersion)GetProcAddress(hNtdll, "RtlGetVersion");
        if (fn_RtlGetVersion) {
            RTL_OSVERSIONINFOW rovi = {0};
            rovi.dwOSVersionInfoSize = sizeof(rovi);
            if (fn_RtlGetVersion(&rovi) == 0) {
                os.buildNumber = rovi.dwBuildNumber;
                std::stringstream ss;
                if (rovi.dwMajorVersion == 10 && rovi.dwBuildNumber >= 22000) {
                    ss << "Windows 11 (Version " << rovi.dwMajorVersion << "." << rovi.dwMinorVersion << ", Build " << rovi.dwBuildNumber << ")";
                } else {
                    ss << "Windows " << rovi.dwMajorVersion << "." << rovi.dwMinorVersion << " (Build " << rovi.dwBuildNumber << ")";
                }
                os.versionString = ss.str();
            }
        }
    }

    // Architecture
    SYSTEM_INFO si;
    GetNativeSystemInfo(&si);
    if (si.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64) {
        os.architecture = "x86_64 (64-bit AMD64)";
    } else if (si.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_INTEL) {
        os.architecture = "x86 (32-bit)";
    } else if (si.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_ARM64) {
        os.architecture = "ARM64";
    } else {
        os.architecture = "Unknown";
    }

    // Compiler Version
#ifdef _MSC_FULL_VER
    os.compilerVersion = "MSVC " + std::to_string(_MSC_FULL_VER);
#elif defined(__clang__)
    os.compilerVersion = "Clang " + std::to_string(__clang_major__) + "." + std::to_string(__clang_minor__);
#elif defined(__GNUC__)
    os.compilerVersion = "GCC " + std::to_string(__GNUC__) + "." + std::to_string(__GNUC_MINOR__);
#else
    os.compilerVersion = "Unknown C++ Compiler";
#endif

    // C++ Language Standard
#if defined(_MSVC_LANG)
    long lang = _MSVC_LANG;
#else
    long lang = __cplusplus;
#endif

    if (lang >= 202002L) os.cppStandard = "C++20 (" + std::to_string(lang) + ")";
    else if (lang >= 201703L) os.cppStandard = "C++17 (" + std::to_string(lang) + ")";
    else if (lang >= 201402L) os.cppStandard = "C++14 (" + std::to_string(lang) + ")";
    else os.cppStandard = "Pre-C++14 (" + std::to_string(lang) + ")";
}

// ============================================================================
// TERMINAL FORMATTER & JSON EXPORTER
// ============================================================================

static void PrintTerminalReport(const SystemInfo& sys) {
    std::cout << "\n================================================================================\n";
    std::cout << "           PC PERFORMANCE BENCHMARK SUITE — PHASE 0 ENVIRONMENT AUDIT          \n";
    std::cout << "================================================================================\n";

    // 1. Operating System & Toolchain
    std::cout << "\n[1. OPERATING SYSTEM & TOOLCHAIN]\n";
    std::cout << "  OS Version:          " << sys.os.versionString << "\n";
    std::cout << "  Architecture:        " << sys.os.architecture << "\n";
    std::cout << "  Active Compiler:     " << sys.os.compilerVersion << "\n";
    std::cout << "  C++ Standard:        " << sys.os.cppStandard << "\n";

    // 2. CPU Telemetry
    std::cout << "\n[2. CPU ARCHITECTURE & TOPOLOGY]\n";
    std::cout << "  Model:               " << sys.cpu.modelName << "\n";
    std::cout << "  Vendor:              " << sys.cpu.vendor << "\n";
    std::cout << "  Physical Cores:      " << sys.cpu.physicalCores << "\n";
    std::cout << "  Logical Processors:  " << sys.cpu.logicalProcessors << " (" 
              << (sys.cpu.logicalProcessors > sys.cpu.physicalCores ? "Hyper-Threading ACTIVE" : "No HT") << ")\n";
    if (sys.cpu.baseFrequencyMHz > 0) {
        std::cout << "  Base Clock (CPUID):  " << sys.cpu.baseFrequencyMHz << " MHz\n";
        std::cout << "  Max Turbo (CPUID):   " << sys.cpu.maxFrequencyMHz << " MHz\n";
        std::cout << "  Bus Reference Clock: " << sys.cpu.busFrequencyMHz << " MHz\n";
    }

    std::cout << "\n  --- Vector & Instruction Set Support ---\n";
    std::cout << "  SSE4.2:   " << (sys.cpu.instructions.at("SSE4.2") ? "[YES]" : "[NO]") 
              << " | AVX:       " << (sys.cpu.instructions.at("AVX") ? "[YES]" : "[NO]")
              << " | AVX2:      " << (sys.cpu.instructions.at("AVX2") ? "[YES]" : "[NO]") << "\n";
    std::cout << "  FMA3:     " << (sys.cpu.instructions.at("FMA3") ? "[YES]" : "[NO]")
              << " | BMI1/BMI2: " << (sys.cpu.instructions.at("BMI1") && sys.cpu.instructions.at("BMI2") ? "[YES]" : "[NO]")
              << " | AES-NI:    " << (sys.cpu.instructions.at("AES-NI") ? "[YES]" : "[NO]") << "\n";
    std::cout << "  AVX-512F: " << (sys.cpu.instructions.at("AVX-512F") ? "[YES]" : "[NO]")
              << " | AVX512-BW: " << (sys.cpu.instructions.at("AVX-512BW") ? "[YES]" : "[NO]")
              << " | AVX512-VL: " << (sys.cpu.instructions.at("AVX-512VL") ? "[YES]" : "[NO]") << "\n";
    std::cout << "  OS State Save:       " 
              << "AVX Enabled = " << (sys.cpu.instructions.at("OS_AVX_Enabled") ? "YES" : "NO") << ", "
              << "AVX-512 Enabled = " << (sys.cpu.instructions.at("OS_AVX512_Enabled") ? "YES" : "NO") << "\n";

    std::cout << "\n  --- CPU Cache Hierarchy ---\n";
    for (size_t i = 0; i < sys.cpu.caches.size(); ++i) {
        const auto& c = sys.cpu.caches[i];
        std::cout << "  L" << c.level << " " << std::left << std::setw(12) << c.type 
                  << " Cache: " << std::right << std::setw(6) << c.sizeKB << " KB"
                  << " (" << c.associativity << "-way, " << c.lineSize << "B line)\n";
    }

    // 3. RAM Telemetry
    std::cout << "\n[3. SYSTEM RAM CONFIGURATION]\n";
    std::cout << "  Total Physical RAM:  " << sys.ram.totalPhysicalMB << " MB (" 
              << std::fixed << std::setprecision(1) << (sys.ram.totalPhysicalMB / 1024.0) << " GB)\n";
    std::cout << "  Available RAM:       " << sys.ram.availablePhysicalMB << " MB (" 
              << std::fixed << std::setprecision(1) << (sys.ram.availablePhysicalMB / 1024.0) << " GB)\n";
    std::cout << "  Current Memory Load: " << sys.ram.memoryLoadPercent << "%\n";
    std::cout << "  Channel Status:      " << sys.ram.channelConfiguration << "\n";

    if (!sys.ram.modules.empty()) {
        std::cout << "  Populated DIMM Modules:\n";
        for (size_t i = 0; i < sys.ram.modules.size(); ++i) {
            const auto& m = sys.ram.modules[i];
            std::cout << "    Slot [" << m.locator << "]: " << m.capacityGB << " GB @ " 
                      << m.configuredSpeedMTs << " MT/s | " << m.manufacturer << " (" << m.partNumber << ")\n";
        }
    }

    // 4. GPU Telemetry
    std::cout << "\n[4. DISCRETE GPU & CUDA TELEMETRY]\n";
    if (sys.gpu.detected) {
        std::cout << "  GPU Model:           " << sys.gpu.name << "\n";
        std::cout << "  NVIDIA Driver:       " << sys.gpu.driverVersion << "\n";
        std::cout << "  CUDA Driver Support: " << sys.gpu.cudaDriverVersionStr << " (API Level " << sys.gpu.cudaDriverVersionRaw << ")\n";
        std::cout << "  Compute Capability:  " << sys.gpu.computeMajor << "." << sys.gpu.computeMinor 
                  << " (Turing TU117)\n";
        std::cout << "  Streaming Multiprocessors: " << sys.gpu.smCount << " SMs (" 
                  << (sys.gpu.smCount * 64) << " CUDA Cores)\n";
        std::cout << "  Warp Size / Max Threads:   " << sys.gpu.warpSize << " / " << sys.gpu.maxThreadsPerBlock << " per block\n";
        std::cout << "  VRAM Capacity:       " << sys.gpu.vramTotalMB << " MB Total | " 
                  << sys.gpu.vramFreeMB << " MB Free | " << sys.gpu.vramUsedMB << " MB Used\n";
        std::cout << "  Memory Bus Width:    " << sys.gpu.memoryBusWidthBits << "-bit (L2 Cache: " << sys.gpu.l2CacheKB << " KB)\n";
        std::cout << "\n  --- Real-Time Idle Sensor Readings (NVML) ---\n";
        std::cout << "  Graphics Core Clock: " << sys.gpu.coreClockMHz << " MHz  (Dynamic Idle State)\n";
        std::cout << "  Memory Clock:        " << sys.gpu.memoryClockMHz << " MHz\n";
        std::cout << "  GPU Temperature:     " << sys.gpu.temperatureC << " °C\n";
        std::cout << "  Current Power Draw:  " << std::fixed << std::setprecision(1) 
                  << sys.gpu.powerUsageWatts << " W / " << sys.gpu.powerLimitWatts << " W (Cap)\n";
    } else {
        std::cout << "  [WARNING] Discrete NVIDIA GPU not responding via NVML or CUDA Driver API.\n";
    }

    std::cout << "\n================================================================================\n";
    std::cout << "           AUDIT COMPLETE — READY FOR BENCHMARK CALIBRATION (PHASE 1)          \n";
    std::cout << "================================================================================\n\n";
}

static void SaveJsonReport(const SystemInfo& sys, const std::string& filepath) {
    // Ensure results directory exists
    CreateDirectoryA("results", nullptr);

    std::ofstream f(filepath);
    if (!f.is_open()) {
        std::cerr << "Failed to open " << filepath << " for writing.\n";
        return;
    }

    f << "{\n";
    f << "  \"timestamp\": \"" << __DATE__ << " " << __TIME__ << "\",\n";
    
    // OS
    f << "  \"os\": {\n";
    f << "    \"name\": \"" << sys.os.osName << "\",\n";
    f << "    \"version\": \"" << sys.os.versionString << "\",\n";
    f << "    \"build\": " << sys.os.buildNumber << ",\n";
    f << "    \"architecture\": \"" << sys.os.architecture << "\",\n";
    f << "    \"compiler\": \"" << sys.os.compilerVersion << "\",\n";
    f << "    \"cpp_standard\": \"" << sys.os.cppStandard << "\"\n";
    f << "  },\n";

    // CPU
    f << "  \"cpu\": {\n";
    f << "    \"model\": \"" << sys.cpu.modelName << "\",\n";
    f << "    \"vendor\": \"" << sys.cpu.vendor << "\",\n";
    f << "    \"physical_cores\": " << sys.cpu.physicalCores << ",\n";
    f << "    \"logical_processors\": " << sys.cpu.logicalProcessors << ",\n";
    f << "    \"base_frequency_mhz\": " << sys.cpu.baseFrequencyMHz << ",\n";
    f << "    \"max_frequency_mhz\": " << sys.cpu.maxFrequencyMHz << ",\n";
    f << "    \"bus_frequency_mhz\": " << sys.cpu.busFrequencyMHz << ",\n";
    f << "    \"instructions\": {\n";
    size_t i = 0;
    for (auto const& [k, v] : sys.cpu.instructions) {
        f << "      \"" << k << "\": " << (v ? "true" : "false");
        if (++i < sys.cpu.instructions.size()) f << ",";
        f << "\n";
    }
    f << "    },\n";
    f << "    \"caches\": [\n";
    for (size_t cIdx = 0; cIdx < sys.cpu.caches.size(); ++cIdx) {
        const auto& c = sys.cpu.caches[cIdx];
        f << "      {\"level\": " << c.level << ", \"type\": \"" << c.type << "\", \"size_kb\": " 
          << c.sizeKB << ", \"associativity\": " << c.associativity << ", \"line_size\": " << c.lineSize << "}";
        if (cIdx + 1 < sys.cpu.caches.size()) f << ",";
        f << "\n";
    }
    f << "    ]\n";
    f << "  },\n";

    // RAM
    f << "  \"ram\": {\n";
    f << "    \"total_mb\": " << sys.ram.totalPhysicalMB << ",\n";
    f << "    \"available_mb\": " << sys.ram.availablePhysicalMB << ",\n";
    f << "    \"load_percent\": " << sys.ram.memoryLoadPercent << ",\n";
    f << "    \"channel_configuration\": \"" << sys.ram.channelConfiguration << "\",\n";
    f << "    \"modules\": [\n";
    for (size_t mIdx = 0; mIdx < sys.ram.modules.size(); ++mIdx) {
        const auto& m = sys.ram.modules[mIdx];
        f << "      {\"slot\": \"" << m.locator << "\", \"capacity_gb\": " << m.capacityGB 
          << ", \"speed_mts\": " << m.configuredSpeedMTs << ", \"manufacturer\": \"" << m.manufacturer 
          << "\", \"part_number\": \"" << m.partNumber << "\"}";
        if (mIdx + 1 < sys.ram.modules.size()) f << ",";
        f << "\n";
    }
    f << "    ]\n";
    f << "  },\n";

    // GPU
    f << "  \"gpu\": {\n";
    f << "    \"detected\": " << (sys.gpu.detected ? "true" : "false") << ",\n";
    f << "    \"name\": \"" << sys.gpu.name << "\",\n";
    f << "    \"driver_version\": \"" << sys.gpu.driverVersion << "\",\n";
    f << "    \"cuda_driver_version\": \"" << sys.gpu.cudaDriverVersionStr << "\",\n";
    f << "    \"compute_capability\": \"" << sys.gpu.computeMajor << "." << sys.gpu.computeMinor << "\",\n";
    f << "    \"sm_count\": " << sys.gpu.smCount << ",\n";
    f << "    \"warp_size\": " << sys.gpu.warpSize << ",\n";
    f << "    \"max_threads_per_block\": " << sys.gpu.maxThreadsPerBlock << ",\n";
    f << "    \"shared_memory_per_block_kb\": " << sys.gpu.sharedMemPerBlockKB << ",\n";
    f << "    \"bus_width_bits\": " << sys.gpu.memoryBusWidthBits << ",\n";
    f << "    \"l2_cache_kb\": " << sys.gpu.l2CacheKB << ",\n";
    f << "    \"vram_total_mb\": " << sys.gpu.vramTotalMB << ",\n";
    f << "    \"vram_free_mb\": " << sys.gpu.vramFreeMB << ",\n";
    f << "    \"vram_used_mb\": " << sys.gpu.vramUsedMB << ",\n";
    f << "    \"idle_core_clock_mhz\": " << sys.gpu.coreClockMHz << ",\n";
    f << "    \"idle_memory_clock_mhz\": " << sys.gpu.memoryClockMHz << ",\n";
    f << "    \"idle_temperature_c\": " << sys.gpu.temperatureC << ",\n";
    f << "    \"idle_power_watts\": " << sys.gpu.powerUsageWatts << ",\n";
    f << "    \"power_limit_watts\": " << sys.gpu.powerLimitWatts << "\n";
    f << "  }\n";
    f << "}\n";

    f.close();
    std::cout << "[INFO] Telemetry successfully exported to: " << filepath << "\n";
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

int main() {
    SystemInfo sys;

    // 1. Audit OS & Compiler Environment
    AuditOs(sys.os);

    // 2. Audit CPU (CPUID + Topology + Caches)
    AuditCpuFeatures(sys.cpu);
    AuditCpuTopologyAndCaches(sys.cpu);

    // 3. Audit RAM (Win32 + WMI)
    AuditRam(sys.ram);

    // 4. Audit GPU (NVML + CUDA Driver API)
    AuditGpu(sys.gpu);

    // 5. Output Results
    PrintTerminalReport(sys);
    SaveJsonReport(sys, "results/system_info.json");

    return 0;
}
