# ============================================================
#  Clean Production Path SKU
# ------------------------------------------------------------
# Name : ExpireML
# CMD  : ExpireML.ps1
# Description : Expire ML on server
# Author : Willy Chiu
# Version : 1.0
# Update : Converted from VBScript to PowerShell
# Date : 03-29-2018
# ============================================================

param()

function Get-Config {
    param(
        [string]$Path = './PRISM_Config.ini'
    )
    $config = @{}
    Get-Content $Path | ForEach-Object {
        if ($_ -match '=') {
            $parts = $_ -split '=', 2
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            $config[$key] = $value
        }
    }
    return $config
}

function Get-SqlConnection {
    param(
        [string]$Server,
        [string]$Database,
        [string]$User,
        [string]$Password
    )
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=$Server;Database=$Database;User ID=$User;Password=$Password;"
    $conn.Open()
    return $conn
}

function Invoke-SqlQuery {
    param(
        [System.Data.SqlClient.SqlConnection]$Connection,
        [string]$Query
    )
    $cmd = $Connection.CreateCommand()
    $cmd.CommandText = $Query
    $da = New-Object System.Data.SqlClient.SqlDataAdapter $cmd
    $dt = New-Object System.Data.DataTable
    [void]$da.Fill($dt)
    return $dt
}

function Execute-SqlNonQuery {
    param(
        [System.Data.SqlClient.SqlConnection]$Connection,
        [string]$Query
    )
    $cmd = $Connection.CreateCommand()
    $cmd.CommandText = $Query
    [void]$cmd.ExecuteNonQuery()
}

function Query-Prism {
    param(
        [string]$Component,
        [System.Collections.Hashtable]$Config,
        [ref]$Result
    )
    $conn = Get-SqlConnection -Server $Config.server -Database $Config.DB -User $Config.ID -Password $Config.PW
    $sql = "select top 1 skunumber,revision,EffectiveDT,skukey from sku where skunumber='"+$Component+"' order by Revision desc"
    $rows = Invoke-SqlQuery -Connection $conn -Query $sql
    if ($rows.Rows.Count -eq 0) {
        $Result.Value += "$Component-----Can't find this component`n"
    } else {
        foreach ($row in $rows) {
            $sku = $row.skunumber
            $rev = $row.revision
            $eff = $row.EffectiveDT
            $Result.Value += "[Before Expire ML] $sku,$rev,$eff`n"
            Update-Prism -Sku $sku -Revision $rev -Config $Config -Result ([ref]$Result.Value)
            if ($Config.Release -eq 'YES') {
                Release-Prism -Sku $sku -Revision $rev -Config $Config
            }
        }
    }
    $conn.Close()
}

function Update-Prism {
    param(
        [string]$Sku,
        [string]$Revision,
        [System.Collections.Hashtable]$Config,
        [ref]$Result
    )
    $conn = Get-SqlConnection -Server $Config.server -Database $Config.DB -User $Config.ID -Password $Config.PW
    $sqlUpdate = "UPDATE sku SET Effectivedt=GetDate(),Expirationdt=GetDate()+7,Endoflife=GetDate()+6 WHERE skunumber='"+$Sku+"' and revision='"+$Revision+"'"
    $sqlSelect = "Select skunumber,revision,EffectiveDT from sku where skunumber='"+$Sku+"' and revision='"+$Revision+"'"
    Execute-SqlNonQuery -Connection $conn -Query $sqlUpdate
    $rows = Invoke-SqlQuery -Connection $conn -Query $sqlSelect
    foreach ($row in $rows) {
        $Result.Value += "[After  Expire ML] $($row.skunumber),$($row.revision),$($row.EffectiveDT)`n"
    }
    $conn.Close()
}

function Release-Prism {
    param(
        [string]$Sku,
        [string]$Revision,
        [System.Collections.Hashtable]$Config
    )
    $conn = Get-SqlConnection -Server $Config.server -Database $Config.DB -User $Config.ID -Password $Config.PW
    $sqlRelease = "DECLARE @Skukey binary(8) select @skukey=skukey from sku where skunumber='"+$Sku+"' and revision='"+$Revision+"' exec sp_ReleaseSku @skukey"
    Execute-SqlNonQuery -Connection $conn -Query $sqlRelease
    $conn.Close()
}

function Write-Result {
    param(
        [string]$Result,
        [string]$TypeServer
    )
    $udate = (Get-Date).ToString('yyyyMMddHHmm')
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $logDir = Join-Path $scriptPath 'Result'
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $logFile = Join-Path $logDir "$TypeServer`_$udate.txt"
    Set-Content -Path $logFile -Value $Result
}

# Main execution
$config = Get-Config
$result = "---------------------------`n|Server Name: $($config.server) |`n|Release to production: $($config.Release)|`n---------------------------`n"
Get-Content './component.txt' | ForEach-Object {
    Query-Prism -Component $_ -Config $config -Result ([ref]$result)
}
Write-Result -Result $result -TypeServer $config.server
Write-Host "Done.."
