from lxml import etree
import os


class ProcessResults():
    def transform_to_html(self, results_xml, xsl, output_html):
        print os.getcwd()
        f = open(xsl)
        o = open(output_html, 'w')
        resultdoc = etree.parse(results_xml)
        rroot = resultdoc.getroot()

        xslt_root = etree.XML(f.read())
        transform = etree.XSLT(xslt_root)
        result_tree = transform(resultdoc)
        o.write(str(result_tree))

if __name__ == "__main__":
    ProcessResults().transform_to_html(results_xml='apps/webdriver_testing/Screenshots/nosetests.xml',
                                       xsl='apps/webdriver_testing/Screenshots/nosetests.xsl',
                                       output_html='apps/webdriver_testing/Screenshots/results.html')
