# Render.ps1 — xuất PDF từ PPTX bằng WPS Presentation COM.
#
# Máy dựng bài không có Microsoft PowerPoint; WPS mở bằng COM "Kwpp.Application".
# Giữ bản PDF làm chuẩn nộp, render chỉ để duyệt nội bộ.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File slides\render.ps1

param(
    [string]$Pptx = "$PSScriptRoot\deck_bao_ve.pptx",
    [string]$Pdf  = "$PSScriptRoot\deck_bao_ve.pdf",
    [string]$Out  = "$PSScriptRoot\render",
    [int]$Dpi = 100
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Pptx)) {
    throw "Không thấy $Pptx — chạy 'python -m slides.build_deck' trước."
}

$wps = New-Object -ComObject Kwpp.Application
$wps.Visible = $true
try {
    $pres = $wps.Presentations.Open($Pptx, $true, $false, $false)
    $pres.SaveAs($Pdf, 32)   # 32 = ppSaveAsPDF
    $pres.Close()
} finally {
    $wps.Quit()
}

Write-Output ("PDF: {0} ({1} byte)" -f $Pdf, (Get-Item $Pdf).Length)

New-Item -ItemType Directory -Force -Path $Out | Out-Null
Get-ChildItem $Out -Filter *.png | Remove-Item -Force

python - @"
import pathlib, pymupdf
out = pathlib.Path(r"$Out")
doc = pymupdf.open(r"$Pdf")
for i, page in enumerate(doc, 1):
    page.get_pixmap(dpi=$Dpi).save(str(out / ("p%02d.png" % i)))
print("da ve", len(doc), "trang")
"@

Write-Output ("PNG: {0}" -f $Out)
