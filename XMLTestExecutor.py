"""
The MIT License (MIT)

Copyright (c) 2014 fh1ch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



import sys
import datetime
import StringIO
import unittest
from xml.sax.saxutils import escape



class StdCapture:
    
    def __init__(self, fpointer):
        self._fpointer = fpointer
        
    def write(self, string):
        self._fpointer.write(self.to_unicode(string))
        
    def writelines(self, string):
        lines = map(self.to_unicode, string)
        self._fpointer.writelines(lines)
        
    def flush(self):
        self._fpointer.flush()
        
    def to_unicode(self, string):
        try:
            return unicode(string)
        except UnicodeDecodeError:
            return string.decode('unicode_escape')

stdOutNew = StdCapture(sys.stdout)
stdErrNew = StdCapture(sys.stderr)



class _ReportGenerator:

    def __init__(self):
        self._report = []
        self.statPassed = 0
        self.statFailed = 0
        self.statError = 0

    def addSuccess(self, test, time, stdData):
        self.statPassed += 1
        strValue = ""
        strValue += self._addSysOut(stdData[0])
        strValue += self._addSysErr(stdData[1])
        self._report.append("""\t\t<testcase classname="%s.%s" name="%s" status="Passed" time="%s">\n%s     </testcase>\n""" % (test.__class__.__module__, test.__class__.__name__, test.id().split('.')[-1], time, strValue)) 

    def addFailure(self, test, err, errStr, time, stdData):
        self.statFailed += 1
        strValue = ""
        strValue += self._addFailureStr(err, errStr)
        strValue += self._addSysOut(stdData[0])
        strValue += self._addSysErr(stdData[1])       
        self._report.append("""\t\t<testcase classname="%s.%s" name="%s" status="Failed" time="%s">\n%s     </testcase>\n""" % (test.__class__.__module__, test.__class__.__name__, test.id().split('.')[-1], time, strValue))  

    def addError(self, test, err, errStr, time, stdData):
        self.statError += 1
        strValue = ""
        strValue += self._addErrorStr(err, errStr)
        strValue += self._addSysOut(stdData[0])
        strValue += self._addSysErr(stdData[1])
        self._report.append("""\t\t<testcase classname="%s.%s" name="%s" status="Error" time="%s">\n%s     </testcase>\n""" % (test.__class__.__module__, test.__class__.__name__, test.id().split('.')[-1], time, strValue))

    def genReport(self, name, time, properties):
        numTests = self.statError + self.statFailed + self.statPassed
        strXMLOut = """<?xml version="1.0" encoding="UTF-8"?>\n"""
        strXMLOut += """<testsuites errors="%s" failures="%s" name="%s" tests="%s" time="%s">\n""" % (self.statError, self.statFailed, name, numTests, time)

        strXMLOut += """\t<testsuite errors="%s" failures="%s" name="%s" tests="%s" >\n""" % (self.statError, self.statFailed, name, numTests)

        if properties and len(properties) > 0:
            strXMLOut += """\t\t<properties>\n"""
            for prop in properties:
                strXMLOut += """\t\t\t<property name="%s" value="%s"/>\n""" % (prop[0], prop[1])
            strXMLOut += """\t\t</properties>\n"""

        for testcase in self._report:
            strXMLOut += testcase

        strXMLOut += """\t</testsuite>\n"""
        strXMLOut += """</testsuites>\n"""
        return strXMLOut
        
    def _addSysOut(self, sysOut):
        strSysOut = ""
        if sysOut != "":
            strSysOut = """\t\t\t<system-out>%s<system-out/>\n""" % escape(sysOut)
        return strSysOut

    def _addSysErr(self, sysErr):
        strSysErr = ""
        if sysErr != "":
            strSysErr = """\t\t\t<system-err>%s<system-err/>\n""" % escape(sysErr)
        return strSysErr

    def _addFailureStr(self, err, errStr):
        return """\t\t\t<failure message="%s" type="%s">%s</failure>\n""" % (err[1], err[0].__name__, escape(errStr[1]))

    def _addErrorStr(self, err, errStr):
        return """\t\t\t<error message="%s" type="%s">%s</error>\n""" % (err[1], err[0].__name__, escape(errStr[1]))

    
 
class _TestCaseResult(unittest.TestResult):

    def __init__(self):
        unittest.TestResult.__init__(self)
        self.result = _ReportGenerator()
        self._stdOutDef = None
        self._stdErrDef = None
        self._stdBuffOut = StringIO.StringIO()
        self._stdBuffErr = StringIO.StringIO()

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self._execStart = datetime.datetime.now()
        self._startCaptureStd()
        
    def stopTest(self, test):
        self._emptyCaptureStd()

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        sys.stderr.write("[OK] " + str(test) + "\n")
        execDur = datetime.datetime.now() - self._execStart
        stdData = self._emptyCaptureStd()
        self.result.addSuccess(test, execDur, stdData)
        
    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        sys.stderr.write("[E] " + str(test) + "\n")
        errStr = self.errors[-1]
        execDur = datetime.datetime.now() - self._execStart
        stdData = self._emptyCaptureStd()
        self.result.addError(test, err, errStr, execDur, stdData)
        
    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        sys.stderr.write("[F] " + str(test) + "\n")
        errStr = self.failures[-1]
        execDur = datetime.datetime.now() - self._execStart
        stdData = self._emptyCaptureStd()
        self.result.addFailure(test, err, errStr, execDur, stdData)

    def _startCaptureStd(self):
        self._stdOutDef = sys.stdout
        self._stdErrDef = sys.stderr
        stdOutNew.fp = self._stdBuffOut
        stdErrNew.fp = self._stdBuffErr
        sys.stdout = stdOutNew
        sys.stderr = stdErrNew
        
    def _emptyCaptureStd(self):
        if self._stdOutDef:
            sys.stdout = self._stdOutDef
            sys.stderr = self._stdErrDef
            self._stdOutDef = None
            self._stdErrDef = None
        return (self._stdBuffOut.getvalue(), self._stdBuffErr.getvalue())



class XMLTestExecutor:

    DEFAULT_REPORT_NAME = "XMLTestExecutor Report"
    VERSION = "0.1.1"

    def __init__(self, stream = sys.stdout, name = None, properties = None):
        self._stream = stream
        if name == None:
            name = self.DEFAULT_REPORT_NAME
        self._name = name
        self._properties = properties
        self._execStart = datetime.datetime.now()

    def run(self, test):
        self._genStartupConsole(self._name, self._properties)
        result = _TestCaseResult()
        test(result)
        self._execStop = datetime.datetime.now()
        self._genReport(result)
        return result

    def _genReport(self, result):
        execDur = self._execStop - self._execStart
        self._genStatisticConsole(result)
        output = result.result.genReport(self._name, execDur, self._properties)
        self._stream.write(output.encode('utf8'))

    def _genStartupConsole(self, name, properties):
        sys.stderr.write("\n\n")
        sys.stderr.write("==============================\n")
        sys.stderr.write("Version: XMLTestExecutor v%s\n" % self.VERSION)
        sys.stderr.write("Report name: %s\n" % name)
        if properties:
            for prop in properties:
                sys.stderr.write("Property: %s - Value: %s\n" % (prop[0], prop[1]))
        sys.stderr.write("Start time: %s\n" % datetime.datetime.now())
        sys.stderr.write("==============================\n\n")

    def _genStatisticConsole(self, result):
        numTests = result.result.statError + result.result.statFailed + result.result.statPassed
        sys.stderr.write("\n\n")
        sys.stderr.write("======= run statistics =======\n")
        sys.stderr.write("Tests passed:  %s\n" % result.result.statPassed)
        sys.stderr.write("Tests failed:  %s\n" % result.result.statFailed)
        sys.stderr.write("Tests errors:  %s\n" % result.result.statError)
        sys.stderr.write("Total tests:   %s\n\n" % numTests)
        sys.stderr.write("Total runtime: %s\n" % (self._execStop - self._execStart))
        sys.stderr.write("==============================\n")



class TestProgram(unittest.TestProgram):

    def runTests(self):
        self.testRunner = XMLTestExecutor()
        unittest.TestProgram.runTests(self)


    
if __name__ == "__main__":
    TestProgram(module = None)
    
