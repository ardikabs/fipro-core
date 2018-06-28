import os
from flask_assets import Bundle

app_css = Bundle('app.css', output='styles/app.css')
app_js = Bundle('app.js', output='scripts/app.js')
materialize_css = Bundle('materialize.css', output='styles/materialize.css')
templates_css = Bundle('style.css', output='styles/templates.css')
theme_css = Bundle('themes/all-themes.css', output='styles/themes/all-themes.css')

templates_js = Bundle('admin.js','demo.js',filters='jsmin',output='scripts/templates.js')
pages_js = Bundle('pages/index.js', output='scripts/pages/index.js')

vendor_css = Bundle(
    'bootstrap/css/bootstrap.css',
    'node-waves/waves.css',
    'animate-css/animate.css',
    'morrisjs/morris.css',
    output='styles/vendor.css')

vendor_js = Bundle(
    'jquery/jquery.min.js',
    'jquery-slimscroll/jquery.slimscroll.js',
    'jquery-countto/jquery.countTo.js',
    'bootstrap/js/bootstrap.js',
    'bootstrap-select/js/bootstrap-select.js',
    'node-waves/waves.js',
    'raphael/raphael.min.js',
    'morrisjs/morris.js',
    'chartjs/Chart.bundle.js',
    'flot-charts/jquery.flot.js',
    'flot-charts/jquery.flot.resize.js',
    'flot-charts/jquery.flot.pie.js',
    'flot-charts/jquery.flot.categories.js',
    'flot-charts/jquery.flot.time.js',
    'jquery-sparkline/jquery.sparkline.js',
    filters='jsmin',
    output='scripts/vendor.js'
)

assets_bundles = dict(
    # app_css = app_css,
    # app_js = app_js,
    materialize_css = materialize_css,
    templates_css = templates_css,
    templates_js = templates_js,
    themes_css = theme_css,
    pages_js = pages_js,
    
    vendor_css = vendor_css,
    vendor_js = vendor_js
)