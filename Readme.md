FluidSound
==========

FluidSound is a research prototype that allows you to index large databases of sounds and interact with them via content-based descriptors from the SuperCollider language.

It is an adaptation for local databases of the Freesound similarity server (https://github.com/MTG/freesound/tree/master/similarity), which uses Essentia and Gaia technologies (http://essentia.upf.edu/).

How to use
==========
The server can be executed using a docker image for simpler handling of dependencies. The following steps have been tested on an OSX machine:

1. Install docker
2. Install the FluidSound.sc class in the SuperCollider extensions folder. Recompile the class library.
3. Copy some audio files to the db/audio folder. Make sure the index folder is empty.
4. Run the indexing script (index_database.sh) from command line. It will take some time depending on the size of the database.
5. Run the server script (run_server.sh)

You should now be able to interact with the database through the same descriptors  used in Freesound: https://freesound.org/docs/api/. FluidSound is similar to Freesound.sc (https://github.com/g-roma/Freesound.sc) but focuses on content-based indexing.

Here's a quick test (run each bit separately in supercollider):

 ```supercollider

 FLSound.getSound(100, {|result|
     ~snd = result;
     ~snd["name"].postln;
 });

 ~snd.getSimilar(action:{|result|
 	result.postln;
 	result[1].name.postln;
 });


 ~snd.getAnalysis(action:{|result|
 	result.postln;
 });


 FLSound.contentSearch(target:".lowlevel.spectral_complexity.mean:2.8", action: {|result|
 	~snd = result[0];
     ~snd["name"].postln;
 });

 ```

 FluidSound can be used as a backend for MIRLC: https://github.com/axambo/MIRLC/
