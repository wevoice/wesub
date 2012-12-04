from lxml import etree
import os
import simplejson


class ProcessResults():
    def transform_to_html(self, results_xml, xsl, output_html):
        print os.getcwd()
        f = open(xsl)
        o = open(output_html, 'w')
        resultdoc = etree.parse(results_xml)
        rroot = resultdoc.getroot()

        bugs = simplejson.load(open(
            'apps/webdriver_testing/Results/known_bugs.json'))

        for el in rroot.iter("testcase"):
            tparts =  el.get("classname").split('.')
            tparts.append(el.get("name"))
            tid = '.'.join(tparts[-3:])

            if tid in bugs.keys():
                bug_list = bugs[tid]
                for bug in bug_list:
                    bug_el = etree.SubElement(el, "bug")
                    bug_el.text = bug
                    el.append(bug_el)
        print(etree.tostring(rroot, pretty_print=True))

        xslt_root = etree.XML(f.read())
        transform = etree.XSLT(xslt_root)
        result_tree = transform(resultdoc)
        o.write(str(result_tree))

if __name__ == "__main__":
    ProcessResults().transform_to_html(
        results_xml='apps/webdriver_testing/Results/nosetests.xml',
        xsl='apps/webdriver_testing/Results/nosetests.xsl',
        output_html='apps/webdriver_testing/Results/results.html')
