# Maintainer: Rishi <rishinamansingh@gmail.com>
pkgname=tree-file-manager
pkgver=0.1.0 
pkgrel=1
pkgdesc="A modern file manager with tree view for Linux systems"
arch=('any')
url="https://github.com/rishibaghel25/tree-file-manager"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-psutil')
makedepends=('python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('YOUR_CHECKSUM_HERE')  # Replace with actual checksum

build() {
    cd "$pkgname-$pkgver"
    python setup.py build
}

package() {
    cd "$pkgname-$pkgver"
    python setup.py install --root="$pkgdir" --optimize=1 --skip-build

    # Install desktop file
    install -Dm644 "$pkgname.desktop" "$pkgdir/usr/share/applications/$pkgname.desktop"

    # Install icon
    install -Dm644 "tree_file_manager/icons/$pkgname.png" "$pkgdir/usr/share/pixmaps/$pkgname.png"

    # Install license
    install -Dm644 "LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}