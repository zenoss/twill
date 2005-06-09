Currently the only testing done is to run a twill script on a testing
Web site.

'test_twill.twill' is the twill script, and 'test_twill.py' is a special
Quixote Web site that tests the twill script.  (Yeah, it's a bit weird.)

To run the tests,

 * make sure Quixote 2.0 or higher is installed;

 * run 'simple_server.py --factory=test_twill.create_publisher';

 * execute 'twill-sh test/test_twill.twill'.

The test will prompt twice for input; just enter something unique each
time.  (These two tests make sure that 'getinput' and 'getpassword' work.)

I hope to add unit testing to twill for version 0.8.
