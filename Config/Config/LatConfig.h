#ifndef LatConfig_h
#define LatConfig_h 

//
// This File has basic interface for the monitoring values
//
//

//
// STL 
#include <string>

// ROOT
#include "Rtypes.h"

// Local
#include "Config/ConfigTuple.h"

class LatConfig {
  
public :
  
  // Standard c'tor, needs a name, this is where the data end up
  // on the output tree
  LatConfig(const char* name):
    m_tree(0),
    m_config(name){
    initConfig();
  }

  // D'tor no-op
  virtual ~LatConfig(){
  }

  // Make the tree
  void latch();

  TTree* makeTree(const std::string& prefix);

  inline TTree* tree() { return m_tree; }

  inline ConfigTuple& tuple() { return m_config; }

protected:

  void initConfig();

private:

  TTree*      m_tree;

  ConfigTuple m_config;

};

#endif

