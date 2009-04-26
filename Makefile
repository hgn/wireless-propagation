
all:
	cd src && $(MAKE) && cd ..;
	python generate.py
	cd latex && $(MAKE) && cd ..;


clean:
	cd src && $(MAKE) clean && cd ..;
	cd latex && $(MAKE) clean && cd ..;
	@rm -f *.gpi
	@rm -f *.dat
	@rm -f *.eps
	@rm -f *.pdf
