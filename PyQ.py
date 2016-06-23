#!/usr/env python
import sys
sys.path.append('data')
import lib3dmm 
import os
from error import LoadError
import glob
from sources import MemorySource
def AddReferenced(quad,quadsource,bucket,addedlist,preprocess):
	if preprocess is not None:
		quad=preprocess('quad',quad)
	outquad=lib3dmm.Quad(quad['type'],quad['id'],quad['mode'],quad['string'])
	for ref in quad['references']:
		if preprocess is not None:
			nref=preprocess('ref',ref)
		else:
			nref=ref
		outquad.addFakeReference(nref['type'],nref['id'],nref['ref_id'])
	outquad.setSource(quad['source'])
	outquad.sortReferences()
	bucket.addQuad(outquad)
	for ref in quad['references']:
		quaddata=(ref['type'],ref['id'])
		fquad=quadsource.find_quad(*quaddata)
		if fquad is None:
			raise LoadError('Couldn\'t find leaf quad to copy: %s:%i' % quaddata)
		if quaddata not in addedlist:
			addedlist.append(quaddata)
			AddReferenced(fquad,quadsource,bucket,addedlist,preprocess)
def CopyTree(source,outfile,quadtype,quadid,preprocess=None):
	outmovie=lib3dmm.c3dmmFileOut()
	outmovie.should_sort=True
	startquad=source.find_quad(quadtype,quadid)
	if startquad is None:
		raise LoadError('Couldn\'t find starting quad to copy: %s:%i' % (quadtype,quadid))
	else:
		addedlist=[]
		AddReferenced(startquad,source,outmovie,addedlist,preprocess)
	outmovie.save(outfile)
def Preprocess(type,quad):
	if type=='quad':
		if quad['type']=='WAVE':
			nquad=dict(quad)
			nquad['source']=MemorySource(wavdata)
			return nquad
		elif quad['type']=='MSND':
			nquad=dict(quad)
			nquad['string']=str(soundname)
			return nquad
	return quad
def exePause():
	if sys.argv[0].endswith('.exe'):
		os.system('pause')
if len(sys.argv)<2:
	print 'PyQ.py version 0.1 by Foone Turing (@foone)'
	print 'Usage: PyQ.py <filename.wav> [filename2.wav] [filename3.wav] [...] [filenameN.wav]'
	print "\nIf you're using the .exe version, you can simply drag a WAV file onto the PyQ.exe file and it'll convert"
	exePause()
	sys.exit()
try:
	infile=None
	for path in ('data/template.3mm.dat','template.3mm.dat'):
		try:
			infile=lib3dmm.c3dmmFile('data/template.3mm.dat')
			break
		except IOError:
			newpath=os.path.join(os.path.dirname(sys.argv[0]),path)
			try:
				infile=lib3dmm.c3dmmFile(newpath)
				break
			except:
				pass
	if infile is None:
		raise IOError('Couldn\'t open template file!')
	files=[]
	for arg in sys.argv[1:]:
		if '*' in arg or '?' in arg:
			files.extend(glob(arg))
		else:
			files.append(arg)
	for wav in files:
		if os.path.exists(wav):
			wavdata=open(wav,'rb').read()
			outname=None
			base,ext=os.path.splitext(wav)
			outname=base+'.3mm'
			if os.path.exists(outname):
				i=1
				while os.path.exists(outname):
					outname=base+'.%i.3mm' % i
					i+=1
				print '%s.3mm exists, saving to %s' % (base,outname)
			soundname=os.path.basename(base)
			CopyTree(infile,outname,'MVIE',0,Preprocess)
			print 'Done with %s => %s' % (wav,outname)
except:
	import traceback
	traceback.print_exc()
	exePause()
