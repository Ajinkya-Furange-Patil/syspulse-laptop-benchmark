param(
    [string]$BinaryPath = "bin\laptop_benchmark.exe"
)

# 1. Locate or create Code Signing Certificate for Ajinkya Furange
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like "*CN=Ajinkya Furange*" } | Select-Object -First 1

if (-not $cert) {
    Write-Host "[INFO] Creating Code Signing Certificate for 'Ajinkya Furange'..."
    $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Ajinkya Furange" -CertStoreLocation "Cert:\CurrentUser\My" -HashAlgorithm SHA256 -NotAfter (Get-Date).AddYears(5)
}

Write-Host "[OK] Using Certificate: $($cert.Subject) [Thumbprint: $($cert.Thumbprint)]"

# 2. Locate SignTool
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
if (Test-Path $signtool) {
    Write-Host "[INFO] Signing $BinaryPath with 'Ajinkya Furange' signature..."
    & $signtool sign /fd SHA256 /sha1 $cert.Thumbprint /d "SysPulse Laptop Benchmark" /du "https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark" $BinaryPath
    Get-AuthenticodeSignature $BinaryPath | Format-List Status, StatusMessage, SignerCertificate
} else {
    Write-Host "[WARNING] signtool.exe not found at $signtool"
}
