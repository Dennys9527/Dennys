' ============================================================
'  Clean Production Path SKU
' ------------------------------------------------------------
' Name : ExpireML
' CMD  : ExpireML.vbs 
' Description :Expire ML on server
' Author : Willy Chiu 
' Version : 1.4
' Update : added explicit variable declarations and cleanup
' Date : 03-29-2018
' ============================================================
Option Explicit

Dim PRISMserver
Dim PRISMDB
Dim PRISMID
Dim PRISMPW
Dim Release
Dim Result_Prism
Dim Count

Count = 0
Config
component
Result_write Result_Prism, PRISMserver
Wscript.Echo "Done.."

'Read config file-----------------------------------------------------------
Sub Config()
    Dim objFSO, objFile, strLine, MyArray
    Set objFSO  = CreateObject("Scripting.FileSystemObject")
    Set objFile = objFSO.OpenTextFile(".\PRISM_Config.ini")
    Do Until objFile.AtEndOfStream
        strLine = objFile.ReadLine
        MyArray = Split(strLine, "=", -1, 1)
        Select Case Trim(MyArray(0))
            Case "server":  PRISMserver = Trim(MyArray(1))
            Case "DB":      PRISMDB = Trim(MyArray(1))
            Case "ID":      PRISMID = Trim(MyArray(1))
            Case "PW":      PRISMPW = Trim(MyArray(1))
            Case "Release": Release = Trim(MyArray(1))
        End Select
    Loop
    objFile.Close
    Result_Prism = "---------------------------" & vbCrLf & _
                   "|Server Name: " & PRISMserver & " |" & vbCrLf & _
                   "|Release to production: " & Release & "|" & vbCrLf & _
                   "---------------------------" & vbCrLf
End Sub

'Read component file-----------------------------------------------------------
Sub component()
    Dim objFSO, objFile, strLine
    Set objFSO  = CreateObject("Scripting.FileSystemObject")
    Set objFile = objFSO.OpenTextFile(".\component.txt")
    Do Until objFile.AtEndOfStream
        strLine = objFile.ReadLine
        PRISMQuery strLine
    Loop
    objFile.Close
End Sub

'Query Prism SKU------------------------------------------------------------------
Sub PRISMQuery(component)
    Dim Connection, Recordset, SQL
    SQL = "select top 1 skunumber,revision,EffectiveDT,skukey from sku where skunumber='" & component & _
          "' order by Revision desc"
    Set Connection = CreateObject("ADODB.Connection")
    Set Recordset  = CreateObject("ADODB.Recordset")
    Connection.Open "Provider=SQLOLEDB;Data Source=" & PRISMserver & ";Trusted_Connection=No;" & _
                    "Initial Catalog=" & PRISMDB & ";User ID=" & PRISMID & ";Password=" & PRISMPW & ";"
    Recordset.Open SQL, Connection
    If Recordset.EOF Then
        Result_Prism = Result_Prism & component & "-----Can't find this component" & vbCrLf
    Else
        Do While Not Recordset.Eof
            Dim PRISMSKU, PRISMREV, EffectiveDT
            PRISMSKU = Recordset("skunumber")
            PRISMREV = Recordset("revision")
            EffectiveDT = Recordset("EffectiveDT")
            Result_Prism = Result_Prism & "[Before Expire ML] " & PRISMSKU & "," & PRISMREV & "," & EffectiveDT & vbCrLf
            PRISMupdate PRISMSKU, PRISMREV
            If UCase(Release) = "YES" Then
                PRISMrelease PRISMSKU, PRISMREV
            End If
            Recordset.MoveNext
        Loop
    End If
    Recordset.Close
    Set Recordset = Nothing
    Connection.Close
    Set Connection = Nothing
End Sub

'Expire Prism SKU------------------------------------------------------------------
Sub PRISMupdate(PRISMSKU, PRISMREV)
    Dim Connection, Recordset, SQLupdate, SQLselect
    SQLupdate = "UPDATE sku SET Effectivedt=GetDate(),Expirationdt=GetDate()+7,Endoflife=GetDate()+6 " & _
                "WHERE skunumber='" & PRISMSKU & "' and revision='" & PRISMREV & "'"
    SQLselect = "Select skunumber,revision,EffectiveDT from sku where skunumber='" & PRISMSKU & _
                "' and revision='" & PRISMREV & "'"
    Set Connection = CreateObject("ADODB.Connection")
    Set Recordset  = CreateObject("ADODB.Recordset")
    Connection.Open "Provider=SQLOLEDB;Data Source=" & PRISMserver & ";Trusted_Connection=No;" & _
                    "Initial Catalog=" & PRISMDB & ";User ID=" & PRISMID & ";Password=" & PRISMPW & ";"
    Connection.Execute SQLupdate
    Recordset.Open SQLselect, Connection
    Do While Not Recordset.Eof
        Dim selectSKU, selectREV, selectEffectiveDT
        selectSKU = Recordset("skunumber")
        selectREV = Recordset("revision")
        selectEffectiveDT = Recordset("EffectiveDT")
        Result_Prism = Result_Prism & "[After  Expire ML] " & selectSKU & "," & selectREV & "," & selectEffectiveDT & vbCrLf
        Count = Count + 1
        Recordset.MoveNext
    Loop
    Recordset.Close
    Set Recordset = Nothing
    Connection.Close
    Set Connection = Nothing
End Sub

'Save result------------------------------------------------------------------
Sub Result_write(result, typesvr)
    Const ForWriting = 2
    Dim udate, path, strLogFile, objFSO, txtStream
    udate = Year(Date) & Month(Date) & Day(Date)
    path = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
    strLogFile = path & "\Result\" & typesvr & "_" & udate & Hour(Time) & Minute(Time) & ".txt"
    Set objFSO = CreateObject("Scripting.FileSystemObject")
    Set txtStream = objFSO.OpenTextFile(strLogFile, ForWriting, True)
    txtStream.WriteLine result
    txtStream.Close
    Set txtStream = Nothing
End Sub

'Release Prism SKU------------------------------------------------------------------
Sub PRISMrelease(PRISMSKU, PRISMREV)
    Dim Connection, SQLrelease
    SQLrelease = "DECLARE @Skukey binary(8) select @skukey=skukey from sku where skunumber='" & PRISMSKU & _
                 "' and revision='" & PRISMREV & "' exec sp_ReleaseSku @skukey"
    Set Connection = CreateObject("ADODB.Connection")
    Connection.Open "Provider=SQLOLEDB;Data Source=" & PRISMserver & ";Trusted_Connection=No;" & _
                    "Initial Catalog=" & PRISMDB & ";User ID=" & PRISMID & ";Password=" & PRISMPW & ";"
    Connection.Execute SQLrelease
    Connection.Close
    Set Connection = Nothing
End Sub
