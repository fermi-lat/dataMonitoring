
//
// stl
#include <string>
#include <fstream>

//
// ROOT-io
#include "TFile.h"
#include "TTree.h"

// local
#include "Config/LatConfig.h"
#include "Config/ConfigReader.h"

//
int main(int argn, char** argc) {


  const std::string nullString;
  LatConfig config("Config");
  
  ConfigReader reader(config.tuple());
  

  TFile fOut("config.root","RECREATE");
  TTree* t = config.makeTree(nullString);

  for (int i(1); i < argn; i++ ) {
    std::cout << argc[i] << std::endl;
    Bool_t ok = reader.read(argc[i]);
    assert(ok);
  }    
  config.latch();
  
  t->Write();
  fOut.Close();

  return 0;
}







