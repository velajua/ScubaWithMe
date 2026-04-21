# chaiNNer CLI Notes

Official docs:

- https://github.com/chaiNNer-org/chaiNNer/wiki/05--CLI

Executable discovery:

```cmd
set CHAINNER_EXE=%LOCALAPPDATA%\chaiNNer\chaiNNer.exe
```

Working command pattern:

```cmd
cmd /c ""%CHAINNER_EXE%" run "%CD%\workflows\CHAIN.chn" > "%CD%\notes\CHAIN.log" 2>&1"
```

Update the current three comparison templates for one image:

```cmd
cmd /c python chainner-template-helper.py update working\current-png\moray1.png
```

Run the current three comparison templates for one image:

```cmd
cmd /c python chainner-template-helper.py run-one working\current-png\fish1.png
```

Run the current three comparison templates for every image in `working/current-png/`:

```cmd
cmd /c python chainner-template-helper.py run-folder
```

Legacy wrapper for the current template state:

```cmd
cmd /c run-chainner-final-templates.cmd
```

Important quirks:

- Redirect stdout/stderr to a log file. Without redirection, chaiNNer 0.25.1 can hit an Electron `EPIPE: broken pipe` console error.
- The CLI runs existing `.chn` files. It does not build chains from command flags.
- The CLI can override text, number, file, and directory inputs, but dropdowns, checkboxes, and generic inputs should be fixed inside the saved chain.
- Hand-authored `.chn` files may warn that the save file was tampered with because the GUI checksum is missing. The chain can still run, but production workflows should be saved from the GUI once finalized.
- Current templates use deterministic resize, color grading, denoise, and sharpening. They do not use AI super-resolution yet.
- `chainner-template-helper.py` keeps the saved templates privacy-safe and creates temporary runtime chains under `.chainner-runtime/` when chaiNNer needs absolute paths.

Current workflow docs:

- `notes/chainner-final-product-templates.md`
- `workflows/scubawithme-template-01-natural-print-prep.chn`
- `workflows/scubawithme-template-02-clean-product-prep.chn`
- `workflows/scubawithme-template-03-vivid-reef-grade.chn`
- `chainner-template-helper.py`
