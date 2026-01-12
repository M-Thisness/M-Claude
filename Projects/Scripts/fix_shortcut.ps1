$shortcuts = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Gemini CLI.lnk",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Claude Code.lnk"
)
$wsh = New-Object -ComObject WScript.Shell
$fixedAny = $false

foreach ($shortcutPath in $shortcuts) {
    if (Test-Path $shortcutPath) {
        $name = [System.IO.Path]::GetFileName($shortcutPath)
        Write-Host "Processing $name..."
        
        $sc = $wsh.CreateShortcut($shortcutPath)
        
        # 1. Set the Working Directory
        $sc.WorkingDirectory = "C:\Users\Mischa\Documents\M-Gemini"
        Write-Host "  - Set Working Directory to: $($sc.WorkingDirectory)"

        # 2. Ensure the window stays open (wrap in cmd /k if not already)
        if ($sc.TargetPath -notmatch "cmd.exe") {
            $originalTarget = $sc.TargetPath
            $originalArgs = $sc.Arguments
            
            $sc.Arguments = "/k ""$originalTarget"" $originalArgs"
            $sc.TargetPath = "C:\Windows\System32\cmd.exe"
            Write-Host "  - Updated Target to keep window open."
        } else {
            if ($sc.Arguments -notmatch "/k") {
                 $sc.Arguments = "/k " + $sc.Arguments
                 Write-Host "  - Added /k to arguments."
            } else {
                 Write-Host "  - Window behavior already correct."
            }
        }

        $sc.Save()
        Write-Host "  - Saved."
        $fixedAny = $true
    }
}

if (-not $fixedAny) {
    Write-Host "No matching shortcuts found to fix."
} else {
    Write-Host "Done."
}
