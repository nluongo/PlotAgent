
ROOTINC = $(shell root-config --cflags)
ROOTLIB = $(shell root-config --libs)


OBJ = AtlasLabels.o AtlasStyle.o AtlasUtils.o

ATLASOBJ = $(OBJS)
BASICOBJ = $(OBJS)

all : atlastest basictest

.SUFFIXES: .C .o

.C.o :
	g++ $(ROOTINC) -c $<

atlastest : $(OBJ)
	g++  -o $@ $(OBJ) $(ROOTLIB)

basictest : $(OBJ)
	g++  -o $@ $(OBJ) $(ROOTLIB)

archive : clean
	cd .. ; tar -czf AtlasStyle.tgz AtlasStyle

clean : 
	rm -rf *.o *~
