import os

if __name__ == '__main__':
    root = r'C:\Users\Al\Downloads'
    kg = [
        'IMG_20211118_102547.jpg',
        'IMG_20211118_102508.jpg',
        'IMG_20211118_102439.jpg'
    ]
    mv = [
        'IMG_20211118_102623.jpg',
        'IMG_20211118_110251.jpg',
        'IMG_20211118_103209.jpg',
        'IMG_20211118_103308.jpg',
        'IMG_20211118_102845.jpg',
        'IMG_20211118_102758.jpg'
        # 'IMG_20211118_102700.jpg'
    ]
    av = [
        'IMG_20211118_104027.jpg',
        'IMG_20211118_104002.jpg',
        'IMG_20211118_103946.jpg',
        'IMG_20211118_103919.jpg',
        'IMG_20211118_103851.jpg',
        'IMG_20211118_103836.jpg',
        'IMG_20211118_103819.jpg',
        'IMG_20211118_103757.jpg',
        '1637234721914.jpg'
    ]
    os.chdir(root)
    docs = [('rp', 'IMG_20211118_104926.jpg'), ('kg', kg), ('mv', mv), ('av', av)]
    quality = 35
    for prefix, files in docs:
        if isinstance(files, str):
            os.system(f'convert {files} -quality {quality} {prefix}.pdf')
        else:
            pages = ''
            for i, f in enumerate(files):
                page = f'{prefix}{i}.pdf'
                pages += page + ' '
                os.system(f'convert {f} -quality {quality} {page}')
            os.system(f'pdftk {pages} cat output {prefix}.pdf')
            os.system(f'del {pages}')

    docs = ' '.join(f'{doc}.pdf' for doc in [
        '1-7un',
        'rp',
        'av',
        'Lisa_Deka',
        'Stromilo',
        'mv',
        'miete_bezahlt',
        'Bescheinigung_KrankenPflegeVersicherung',
        'kg'
    ])
    os.system(f'pdftk {docs} cat output Lisa_Aufenthalt.pdf')
