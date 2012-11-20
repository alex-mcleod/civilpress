import sys
from subprocess import call

'''
Essentially a wrapper for the DocumentConverter.py script (downloaded from GitHub) located in OpenOffice folder and the pdf2swf application. Allows conversion between all document 
formats supported by OpenOffice, and conversion from pdf files to swf files (via the pdf2swf program). NOTE: Conversion from pdf to pdf currently produces unreadable output. This should
be fixed so that users can upload pdf files to CivilPress.org. 
'''

open_office_location = r'"/usr/lib/libreoffice/program/soffice"'
open_office_python_location = r'"/usr/bin/python2.7"'
document_converter_location = r'"/usr/lib/libreoffice/program/DocumentConverter.py"' 

def convert_document(in_doc, out_doc):
	#try: Service should already be started. 
	    # Starts Open  Office service.
	 #   retcode = call(open_office_location + ' ' + r'"-accept=socket,port=2002;urp"', shell=True)
	  #  if retcode < 0:
	#	print >>sys.stderr, "Start Open Office service was terminated by signal", -retcode
	 #   else:
	#	print >>sys.stderr, "Start Open Office service returned", retcode
	#except OSError, e:
	 #   print >>sys.stderr, "Start Open Office service failed:", e
	try: 
	    # Runs document_converter.py using Open Office service.       
	    retcode = call(open_office_python_location + ' ' + document_converter_location + ' ' + in_doc + ' ' + out_doc, shell=True) 
	    if retcode < 0:
		print >>sys.stderr, "DocumentConverter.py was terminated by signal", -retcode
	    else:
		print >>sys.stderr, "DocumentConverter.py returned", retcode
	except OSError, e:
	    print >>sys.stderr, "DocumentConverter.py failed:", e
	# NOTE: OpenOffice service is not terminated, however document is closed by DocumentConverter.py. Probably no need to terminate OpenOffice service as otherwise will just need to start it again. 

pdf_to_swf_location = r'"pdf2swf"'

def pdf_to_swf(in_doc, out_doc):
	try:
	    print >>sys.stderr, pdf_to_swf_location + '" "' + in_doc + '" -o "' + out_doc + '" "' + r'"-T 9 -f"'
	    # Starts pdf2swf and converts in_doc to out_doc
	    retcode = call(pdf_to_swf_location + ' ' + in_doc + ' ' + '-o' + ' ' + out_doc + ' ' + r'"-T 9 -f"', shell=True) 
	    if retcode < 0:
		print >>sys.stderr, "Start pdf2swf was terminated by signal", -retcode
	    else:
		pass
		#print >>sys.stderr, "Start pdf2swf returned", retcode
	except OSError, e:
	    print >>sys.stderr, "Start pdf2swf failed:", e
