# Define output directory
$outputDir = if ($env:OUTPUT_DIR) { $env:OUTPUT_DIR } else { "data\screenshots" }

# Create the directory if it doesn't exist
if (-not (Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Get the interval from the first argument or 5 seconds
$interval = if ($args.Count -gt 0) { [int]$args[0] } else { 5 }

# Add necessary types for Windows API calls
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class User32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
}

public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}
"@

function Take-Screenshot {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $filename = Join-Path -Path $outputDir -ChildPath "screenshot_$timestamp.png"

    # Load necessary assemblies
    Add-Type -AssemblyName System.Drawing

    # Get the handle of the active window
    $hWnd = [User32]::GetForegroundWindow()

    # Get the dimensions of the active window
    $rect = New-Object RECT
    if (-not [User32]::GetWindowRect($hWnd, [ref]$rect)) {
        Write-Host "Failed to get window rect."
        return
    }

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    # Capture the active window
    try {
        $bitmap = New-Object System.Drawing.Bitmap $width, $height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, [System.Drawing.Size]::new($width, $height))
        $bitmap.Save($filename, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Host "Screenshot saved: $filename"
        $graphics.Dispose()
        $bitmap.Dispose()
    } catch {
        Write-Host "Failed to save screenshot: $_"
    }
}

while ($true) {
    Take-Screenshot
    Start-Sleep -Seconds $interval
}
