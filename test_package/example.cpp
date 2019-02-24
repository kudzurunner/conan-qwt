#include <iostream>
#include <qwt_global.h>
#include <qwt_plot_curve.h>

int main() {
    std::cout << "qwt version: " << QWT_VERSION_STR << std::endl;
    QwtPlotCurve curve("curve");
    return 0;
}
