$total = '\ffmpeg\bin'
$cwd = Get-Location
$new = $cwd -as [String]
$all = $new + $total
echo $all
[Environment]::SetEnvironmentVariable('PATH', [Environment]::GetEnvironmentVariable('PATH', 'User') + ";$all", 'User')