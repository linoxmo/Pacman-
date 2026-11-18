# PyInstaller spec: "make package" builds dist/pac-man, one file with the
# code, the images and the libraries (run it with: ./pac-man config.json)

a = Analysis(
    ["pac-man.py"],
    datas=[("images", "images")],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="pac-man",
    console=True,
    upx=False,
)
