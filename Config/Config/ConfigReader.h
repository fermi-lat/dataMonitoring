#ifndef ConfigReader_h
#define ConfigReader_h 

//
// This File has basic interface for the monitoring values
//
//

//
// STL 
#include <string>

// ROOT
#include "Rtypes.h"

// XML
#include "xmlBase/Dom.h"
#include <xercesc/dom/DOMElement.hpp>


// Forward declare
class ConfigTuple;
class ChannelKey;

//
// 
// Base class for Branches
//

using namespace xmlBase;

class ConfigReader {
  
public :
  
  // Standard c'tor, needs a name, this is where the data end up
  // on the output tree
  ConfigReader(ConfigTuple& tuple)
    :m_config(&tuple),
     _iAFE(-1),_iARC(-1),     
     _iTEM(-1),
     _iCCC(-1),_iCRC(-1),_iCFE(-1),
     _iSPT(-1),_iTFE(-1),
     _iTCC(-1),_iTRC(-1){}

  // D'tor, no-op
  virtual ~ConfigReader(){
  }

  Bool_t read(const std::string& fileName);

protected:

  Bool_t read_AEM(DOMElement& elem);
  Bool_t read_AFE(DOMElement& elem);
  Bool_t read_ARC(DOMElement& elem);
  Bool_t read_TEM(DOMElement& elem);
  Bool_t read_CCC(DOMElement& elem);
  Bool_t read_CRC(DOMElement& elem);
  Bool_t read_CFE(DOMElement& elem);
  Bool_t read_SPT(DOMElement& elem);
  Bool_t read_TFE(DOMElement& elem);
  Bool_t read_TDC(DOMElement& elem);
  Bool_t read_TCC(DOMElement& elem);
  Bool_t read_TRC(DOMElement& elem);
  Bool_t read_GEM(DOMElement& elem);

  Bool_t getId(DOMElement& elem, Int_t& id);
  Bool_t getUShort(DOMElement& elem, UShort_t& val);
  Bool_t getUInt(DOMElement& elem, UInt_t& val);
  Bool_t getULong(DOMElement& elem, ULong64_t& val);

  Bool_t readUShort(DOMElement& elem, const ChannelKey& key, const char* bName = 0);
  Bool_t readUInt(DOMElement& elem, const ChannelKey& key, const char* bName = 0);
  Bool_t readULong(DOMElement& elem, const ChannelKey& key, const char* bName = 0);

  Int_t getIndex(DOMElement& elem, const std::string& rootName);
  Bool_t getSptId(DOMElement& elem, Int_t& id);
private:

  
  ConfigTuple* m_config;

  Int_t _iAFE;
  Int_t _iARC;

  Int_t _iTEM;
  Int_t _iCCC;
  Int_t _iCRC;
  Int_t _iCFE;

  Int_t _iSPT;
  Int_t _iTFE;
  Int_t _iTCC;
  Int_t _iTRC;

};

#endif
