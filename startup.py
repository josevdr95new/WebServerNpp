# -*- coding: utf-8 -*-

# ====================================================================
# SECTION TO ADD TO startup.py
# Enables ws commands: startws(), stopws(), statusws(), refreshws()
# to control WebServerNpp.py
# ====================================================================

import sys
import os

script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)
    print "[Startup] Scripts directory added to path: {}".format(script_dir)

try:
    import WebServerNpp
    from Npp import console

    def startws():
        """Start the web server from console."""
        if 'console' in globals():
            console.show()
            console.write(">>> Executing startws()...\n")
        else:
            print ">>> Executing startws()... (Npp console not available)"
        try:
            WebServerNpp.start_web_server()
            if 'console' in globals(): console.write(">>> startws() completed.\n")
            else: print ">>> startws() completed."
        except Exception as e:
            if 'console' in globals(): console.error(">>> Error in startws(): {}\n".format(e))
            else: print ">>> Error in startws(): {}".format(e)

    def stopws():
        """Stop the web server from console."""
        if 'console' in globals():
            console.show()
            console.write(">>> Executing stopws()...\n")
        else:
            print ">>> Executing stopws()... (Npp console not available)"
        try:
            WebServerNpp.stop_web_server()
            if 'console' in globals(): console.write(">>> stopws() completed.\n")
            else: print ">>> stopws() completed."
        except Exception as e:
            if 'console' in globals(): console.error(">>> Error in stopws(): {}\n".format(e))
            else: print ">>> Error in stopws(): {}".format(e)

    def statusws():
        """Show web server status from console."""
        if 'console' in globals():
            console.show()
            console.write(">>> Executing statusws()...\n")
        else:
            print ">>> Executing statusws()... (Npp console not available)"
        try:
            WebServerNpp.show_server_status()
            if 'console' in globals(): console.write(">>> statusws() completed.\n")
            else: print ">>> statusws() completed."
        except Exception as e:
            if 'console' in globals(): console.error(">>> Error in statusws(): {}\n".format(e))
            else: print ">>> Error in statusws(): {}".format(e)

    def refreshws():
        """Restart web server with current active file's directory."""
        if 'console' in globals():
            console.show()
            console.write(">>> Executing refreshws()...\n")
        else:
            print ">>> Executing refreshws()... (Npp console not available)"
        try:
            WebServerNpp.refresh_web_server()
            if 'console' in globals():
                console.write(">>> refreshws() completed.\n")
            else:
                print ">>> refreshws() completed."
        except Exception as e:
            if 'console' in globals():
                console.error(">>> Error in refreshws(): {}\n".format(e))
            else:
                print ">>> Error in refreshws(): {}".format(e)

    print "[WebServerNpp Startup] Console commands ready: startws(), stopws(), statusws(), refreshws()"
    if 'console' in globals():
        console.write("Web server commands ready: startws(), stopws(), statusws(), refreshws()\n")

except ImportError as e:
    print "[WebServerNpp Startup] Import error: {}. Ensure WebServerNpp.py exists.".format(e)
    if 'console' in globals():
        console.error("[WebServerNpp Startup] Import error: {}. Commands unavailable.\n".format(e))
except Exception as e:
    import traceback
    print "[WebServerNpp Startup] Unexpected initialization error: {}".format(e)
    print traceback.format_exc()
    if 'console' in globals():
        console.error("[WebServerNpp Startup] Unexpected initialization error: {}\n".format(e))
        console.error(traceback.format_exc() + "\n")

# --- End of WebServerNpp section ---
# ====================================================================