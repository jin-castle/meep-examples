param(
  [Parameter(Mandatory = $true)][string]$Frames,
  [string]$Url = 'http://127.0.0.1:8739/',
  [string]$CaptureScript = 'C:/Users/bgs43/.claude/skills/photonics-motion/scripts/render_loop.mjs',
  [string]$Ffmpeg = '',
  [string]$Ffprobe = ''
)
$ErrorActionPreference = 'Stop'
if (-not $Ffmpeg) {
  $foundFfmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
  if ($foundFfmpeg) { $Ffmpeg = $foundFfmpeg.Source }
  else { $Ffmpeg = Join-Path $env:LOCALAPPDATA 'Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe' }
}
if (-not (Test-Path -LiteralPath $Ffmpeg -PathType Leaf)) { throw 'FFmpeg executable missing; pass -Ffmpeg <path>' }
if (-not $Ffprobe) {
  $foundFfprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
  if ($foundFfprobe) { $Ffprobe = $foundFfprobe.Source }
  else { $Ffprobe = Join-Path (Split-Path -Parent $Ffmpeg) 'ffprobe.exe' }
}
if (-not (Test-Path -LiteralPath $Ffprobe -PathType Leaf)) { throw 'FFprobe executable missing; pass -Ffprobe <path>' }
# Use a fresh frame folder when scene.js changes: the capture tool resumes existing PNGs.
node $CaptureScript $Url $Frames --w 1280 --h 720 --fps 30 --seconds 8
if ($LASTEXITCODE -ne 0) { throw 'Frame capture failed' }
$assetFolder = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../assets/meep/16'))
$sequence = Join-Path $Frames 'f_%04d.png'
$poster = Join-Path $Frames 'f_0120.png'
& $Ffmpeg -y -loglevel error -framerate 30 -i $sequence -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart -an (Join-Path $assetFolder '00_intro.mp4')
if ($LASTEXITCODE -ne 0) { throw 'Video encoding failed' }
& $Ffmpeg -y -loglevel error -i $poster -q:v 4 (Join-Path $assetFolder '00_intro.jpg')
if ($LASTEXITCODE -ne 0) { throw 'Poster encoding failed' }
& $Ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,duration -show_entries format=duration,size -of json (Join-Path $assetFolder '00_intro.mp4')
if ($LASTEXITCODE -ne 0) { throw 'FFprobe validation failed' }
