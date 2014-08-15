XMLTestExecutor
===============
Simple and lightweight XML unittest runner for Python with test-suite support.

## Goal
The intention of XMLTestExecutor is to support the [jUnit XML format][1] including the property tags, but also be lightweight and easy to use at the same time. The second goal is to provide full compatibility of the reports with build systems likes [Jenkins][2]. The project was designed and also tested to fit these needs. Another important feature is the execution of multiple unittests which are combined in one test-suite.

## License
This project is licensed under the MIT license. Please check out the [LICENSE.md](/LICENSE.md/) file for more information.

## Usage
The usage is quiet simple. Just include [XMLTestExecutor.py](/XMLTestExecutor.py/) into your own project: 
``` python
import XMLTestExecutor
```
And replace the default Python unittest runner with the XMLTestExecutor like this:
``` python
fpointer = file("testReport.xml", "wb")
runner = XMLTestExecutor.XMLTestExecutor(stream=fpointer, name="XMLTestExecutor example report")
runner.run(testSuit)
```
XMLTestExecutor does also support the property tags provided by the [jUnit XML format][1]. You can set the property tags by using:
``` python
props = [("Target", "TestVM01"), ("Version", "01.33.215"), ("Branch", "NIGHTLY")]
runner = XMLTestExecutor.XMLTestExecutor(stream=fpointer, properties=props, name='XMLTestExecutor example report')
```
Beneath the report provided by the stream parameter, XMLTestExecutor will also print metadata like the properties, test name and the statistical results to the console. If no stream is provided, XMLTestExecutor will print the report to the console as well.

[1]: https://svn.jenkins-ci.org/trunk/hudson/dtkit/dtkit-format/dtkit-junit-model/src/main/resources/com/thalesgroup/dtkit/junit/model/xsd/junit-4.xsd "jUnit XML format"
[2]: http://jenkins-ci.org/ "Jenkins CI"