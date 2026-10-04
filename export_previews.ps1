$pptPath = (Get-Item "llama_cpp_20min_praesentation.pptx").FullName
$outDir = Join-Path (Get-Location) "slide_previews"
if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$ppt = New-Object -ComObject PowerPoint.Application
$presentation = $ppt.Presentations.Open($pptPath, 1, 0, 0)

$count = $presentation.Slides.Count
for ($i = 1; $i -le $count; $i++) {
    $outFile = Join-Path $outDir ("slide_{0:d2}.png" -f $i)
    $presentation.Slides.Item($i).Export($outFile, "PNG", 1920, 1080)
}

$presentation.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Host "Exported $count slides to $outDir"
