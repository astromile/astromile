Write "Jupyter Notebooks Cleaner"
conda activate base

Get-ChildItem -Path ../python/*.ipynb -Recurse | ForEach-Object{
    jupyter nbconvert --ClearMetadataPreprocessor.enabled=True --clear-output $_
    # (..) - forces Get-Content to read the whole file into memory => can be overwritten
    ((Get-Content $_) -join "`n") + "`n" | Set-Content -NoNewline $_
}
