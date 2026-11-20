$ErrorActionPreference = 'Stop'
$word = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
try {
    [Console]::WriteLine(('WORD_ACTIVE version={0} documents={1} hwnd={2}' -f $word.Version,$word.Documents.Count,$word.Hwnd))
} finally {
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
