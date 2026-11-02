<#
.SYNOPSIS
    Script otomatis untuk mengompresi tugas mingguan menjadi berkas <NIM>-m<minggu>.zip
    sesuai standar perkuliahan Kapita Selekta: AI Engineering.

.DESCRIPTION
    Script ini mengambil isi folder m1..m7 di dalam folder 'Tugas Mingguan' dan mengemasnya
    ke dalam format ZIP: <NIM>-m<minggu>.zip tanpa nesting folder berlebih.

.PARAMETER NIM
    Nomor Induk Mahasiswa Anda (contoh: 1201230045)

.PARAMETER Minggu
    Nomor minggu yang ingin dikompres (1 sampai 7)

.PARAMETER All
    Jika diaktifkan, akan mengompres seluruh minggu dari 1 sampai 7 secara berurutan.

.EXAMPLE
    .\package-tugas.ps1 -NIM "1201230045" -Minggu 1
    Mengompres isi folder m1 menjadi 1201230045-m1.zip

.EXAMPLE
    .\package-tugas.ps1 -NIM "1201230045" -All
    Mengompres seluruh folder m1 s/d m7 menjadi zip terpisah
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false, HelpMessage = "Masukkan NIM Anda")]
    [string]$NIM,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 7)]
    [int]$Minggu,

    [Parameter(Mandatory = $false)]
    [switch]$All
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Prompt NIM jika belum diisi
if ([string]::IsNullOrWhiteSpace($NIM)) {
    $NIM = Read-Host "Masukkan NIM Anda (contoh: 1201230045)"
    if ([string]::IsNullOrWhiteSpace($NIM)) {
        Write-Error "NIM tidak boleh kosong! Operasi dibatalkan."
        exit 1
    }
}

# Tentukan daftar minggu yang akan dikemas
$TargetWeeks = @()
if ($All) {
    $TargetWeeks = 1..7
} elseif ($Minggu) {
    $TargetWeeks = @($Minggu)
} else {
    $Pilihan = Read-Host "Pilih nomor minggu (1-7) atau ketik 'all' untuk semua"
    if ($Pilihan.ToLower() -eq 'all') {
        $TargetWeeks = 1..7
    } else {
        $W = 0
        if ([int]::TryParse($Pilihan, [ref]$W) -and ($W -ge 1 -and $W -le 7)) {
            $TargetWeeks = @($W)
        } else {
            Write-Error "Nomor minggu tidak valid (harus 1-7 atau 'all'). Operasi dibatalkan."
            exit 1
        }
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Pengemas Tugas Mingguan: Kapita Selekta AI Engineering  " -ForegroundColor Cyan
Write-Host "  NIM: $NIM" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

foreach ($w in $TargetWeeks) {
    $FolderSrc = Join-Path $ScriptDir "m$w"
    $ZipName = "$NIM-m$w.zip"
    $ZipDest = Join-Path $ScriptDir $ZipName

    if (-not (Test-Path $FolderSrc)) {
        Write-Warning "[SKIP] Folder sumber '$FolderSrc' tidak ditemukan."
        continue
    }

    # Verifikasi keberadaan file wajib
    $CatatanProses = Join-Path $FolderSrc "catatan-proses.md"
    $FolderBukti = Join-Path $FolderSrc "bukti"

    Write-Host "`n--> Memeriksa kelengkapan berkas Minggu $w..." -ForegroundColor Green
    if (-not (Test-Path $CatatanProses)) {
        Write-Warning "    [PERINGATAN] 'catatan-proses.md' tidak ditemukan di m$w!"
    } else {
        Write-Host "    [OK] catatan-proses.md tersedia." -ForegroundColor Gray
    }

    if (-not (Test-Path $FolderBukti)) {
        Write-Warning "    [PERINGATAN] Folder 'bukti/' tidak ditemukan di m$w!"
    } else {
        Write-Host "    [OK] folder bukti/ tersedia." -ForegroundColor Gray
    }

    # Hapus file ZIP lama jika ada
    if (Test-Path $ZipDest) {
        Remove-Item -Path $ZipDest -Force
    }

    # Proses kompresi
    Write-Host "--> Mengompres isi 'm$w' ke '$ZipName'..." -ForegroundColor Cyan
    try {
        # Ambil seluruh item di dalam m<w> agar tidak membuat folder pembungkus ekstra
        $Items = Get-ChildItem -Path $FolderSrc
        Compress-Archive -Path $Items.FullName -DestinationPath $ZipDest -Force
        
        $ZipItem = Get-Item $ZipDest
        $SizeKB = [math]::Round($ZipItem.Length / 1KB, 2)
        Write-Host "    [SUKSES] Berkas berhasil dibuat: $ZipName ($SizeKB KB)" -ForegroundColor Green
        Write-Host "    Lokasi: $ZipDest" -ForegroundColor Gray
    } catch {
        Write-Error "    [GAGAL] Gagal mengompres m$($w): $_"
    }
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "Selesai! Pastikan memeriksa isi ZIP sebelum mengunggah." -ForegroundColor Yellow
Write-Host "==========================================================`n" -ForegroundColor Cyan
