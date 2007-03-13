
#include "Config/ConfigReader.h"

#include "Config/ConfigTuple.h"

#include "xmlBase/Dom.h"
#include "xmlBase/XmlParser.h"
#include <xercesc/dom/DOMNode.hpp>

using namespace xmlBase;


Bool_t ConfigReader::read(const std::string& fileName) {
  XmlParser parser( true );
  DOMDocument* doc(0);
  try {
    doc = parser.parse( fileName.c_str() );
  } 
  catch (ParseException ex) {
    std::cout << "caught exception with message " << std::endl;
    std::cout << ex.getMsg() << std::endl;
    return kFALSE;
  }
  DOMElement* topElt = doc->getDocumentElement();
  
  std::vector<DOMElement*> eltList;
  std::vector<DOMElement*>::iterator itr = eltList.begin();  

  Dom::getChildrenByTagName( topElt, "AEM", eltList );
  for ( itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( read_AEM(**itr) == kFALSE ) return kFALSE;    
  }
  Dom::getChildrenByTagName( topElt, "TEM", eltList );
  for ( itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( read_TEM(**itr) == kFALSE ) return kFALSE;    
  }
  Dom::getChildrenByTagName( topElt, "GEM", eltList );
  for ( itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( read_GEM(**itr) == kFALSE ) return kFALSE;    
  }
  return kTRUE;
}

Bool_t ConfigReader::read_AEM(DOMElement& elem) {
  const std::string ARC("ARC");  
  ChannelKey key(0);
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,ARC) ) {
      if ( read_ARC(**itr) == kFALSE ) return kFALSE;    
    } else {
      if ( ! readUInt(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
}

Bool_t ConfigReader::read_ARC(DOMElement& elem) {  
  const std::string AFE("AFE");
  const std::string pha("pha_threshold");
  if ( ! ConfigReader::getId(elem,_iARC) ) return kFALSE;
  ChannelKey key(_iARC);
  std::vector<DOMElement*> eltList;
  //std::cout << Dom::getTagName(&elem) << std::endl;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,AFE) ) {
      if ( read_AFE(**itr) == kFALSE ) return kFALSE;
      continue;
    }  else if ( Dom::getTagName(*itr).find(pha) == ! std::string::npos ) {
      Int_t idx = getIndex(**itr,pha);
      ChannelKey keyPha(_iARC,idx);
      if ( ! readUShort(**itr,keyPha,pha.c_str()) ) {
	continue;
      }
    } else {
      if ( ! readUShort(**itr,key) ) {
	continue;
      }
    } 
  } 
  return kTRUE;
}

Bool_t ConfigReader::read_AFE(DOMElement& elem) {
  if ( ! ConfigReader::getId(elem,_iAFE) ) return kFALSE;
  ChannelKey key(_iARC,_iAFE);  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  //std::cout << Dom::getTagName(&elem) << std::endl;
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( ! readUShort(**itr,key) ) {
      continue;
    }
  }
  return kTRUE;
}


Bool_t ConfigReader::read_TEM(DOMElement& elem){
  if ( ! ConfigReader::getId(elem,_iTEM) ) return kFALSE;
  ChannelKey key(_iTEM);  
  const std::string SPT("SPT");
  const std::string TIC("TIC");
  const std::string TCC("TCC");
  const std::string CCC("CCC");  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,SPT) ) {
      if ( read_SPT(**itr) == kFALSE ) return kFALSE;    
    } else if  ( Dom::checkTagName(*itr,TIC) ) {
      continue;
    } else if  ( Dom::checkTagName(*itr,TCC) ) {
      if ( read_TCC(**itr) == kFALSE ) return kFALSE; 
    } else if  ( Dom::checkTagName(*itr,CCC) ) {
      if ( read_CCC(**itr) == kFALSE ) return kFALSE; 
    } else {
      if ( ! readUInt(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
}

Bool_t ConfigReader::read_CCC(DOMElement& elem){
  if ( ! ConfigReader::getId(elem,_iCCC) ) return kFALSE;
  ChannelKey key(_iTEM,_iCCC);  
  const std::string CRC("CRC");  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,CRC) ) {
      if ( read_CRC(**itr) == kFALSE ) return kFALSE;    
    } else {
      if ( ! readUInt(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_CRC(DOMElement& elem){
  if ( ! ConfigReader::getId(elem,_iCRC) ) return kFALSE;
  ChannelKey key(_iTEM,_iCCC,_iCRC);  
  const std::string CFE("CFE");  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,CFE) ) {
      if ( read_CFE(**itr) == kFALSE ) return kFALSE;    
    } else {
      if ( ! readUInt(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_CFE(DOMElement& elem){
  if ( ! ConfigReader::getId(elem,_iCFE) ) return kFALSE;
  ChannelKey key(_iTEM,_iCCC,_iCRC,_iCFE);  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  //std::cout << Dom::getTagName(&elem) << std::endl;
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( ! readUInt(**itr,key) ) {
      continue;
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_SPT(DOMElement& elem){
  if ( ! ConfigReader::getSptId(elem,_iSPT) ) return kFALSE;
  ChannelKey key(_iTEM,_iSPT);  
  const std::string TFE("TFE");  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,TFE) ) {
      if ( read_TFE(**itr) == kFALSE ) return kFALSE;    
    } else {
      if ( ! readUInt(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_TFE(DOMElement& elem){
  if ( ! ConfigReader::getId(elem,_iTFE) ) return kFALSE;
  ChannelKey key(_iTEM,_iSPT,_iTFE);  
  const std::string TDC("TDC");  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  //std::cout << Dom::getTagName(&elem) << std::endl;
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,TDC) ) {
      if ( read_TDC(**itr) == kFALSE ) return kFALSE;    
    } else {
      if ( ! readULong(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_TDC(DOMElement& elem){
  ChannelKey key(_iTEM,_iSPT,_iTFE);
  DOMElement* tfe_dac = Dom::findFirstChildByName( &elem, "tfe_dac");
  std::vector<DOMElement*> eltList;  
  Dom::getChildrenByTagName( tfe_dac, "*", eltList );
  //std::cout << Dom::getTagName(&elem) << std::endl;
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( ! readUInt(**itr,key) ) {
      continue;
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_TCC(DOMElement& elem){
  if ( ! ConfigReader::getId(elem,_iTCC) ) return kFALSE;
  ChannelKey key(_iTEM,_iTCC);  
  const std::string TRC("TRC");  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  //std::cout << Dom::getTagName(&elem) << std::endl;
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( Dom::checkTagName(*itr,TRC) ) {
      if ( read_TRC(**itr) == kFALSE ) return kFALSE;    
    } else {
      if ( ! readUInt(**itr,key) ) {
	continue;
      }
    }
  }
  return kTRUE;
    
};

Bool_t ConfigReader::read_TRC(DOMElement& elem){
  ChannelKey key(_iTEM,_iTCC,_iTRC);  
  std::vector<DOMElement*> eltList;
  Dom::getChildrenByTagName( &elem, "*", eltList );
  //std::cout << Dom::getTagName(&elem) << std::endl;
  for ( std::vector<DOMElement*>::iterator itr = eltList.begin(); itr != eltList.end(); itr++ ) {
    if ( ! readUInt(**itr,key) ) {
      continue;
    }
  }
  return kTRUE;
};

Bool_t ConfigReader::read_GEM(DOMElement& /* elem */){
  return kTRUE;
};

Bool_t ConfigReader::getId(DOMElement& elem, Int_t& id) {
  id = ChannelKey::UNDEF;
  std::string ID("ID");
  std::string BCAST("BCAST");
  if ( Dom::getAttribute(&elem,ID) == BCAST ) {
    id = ChannelKey::BCAST;
    return kTRUE;    
  }
  id = Dom::getIntAttribute(&elem,ID);
  return kTRUE;
}

Bool_t ConfigReader::getUShort(DOMElement& elem, UShort_t& val) {
  char** nullPtr(0);
  std::string str = Dom::getTextContent( &elem );
  // should add check
  val = (UShort_t)(strtol(str.c_str(),nullPtr,0));
  return kTRUE;
}

Bool_t ConfigReader::getUInt(DOMElement& elem, UInt_t& val) {
  char** nullPtr(0);
  std::string str = Dom::getTextContent(&elem);
  // should add check
  val = (UInt_t)strtol(str.c_str(),nullPtr,0);
  return kTRUE;
}

Bool_t ConfigReader::getULong(DOMElement& elem, ULong64_t& val) {
  char** nullPtr(0);
  std::string str = Dom::getTextContent(&elem);
  // should add check
  val = strtol(str.c_str(),nullPtr,0);
  return kTRUE;
}


Bool_t ConfigReader::readUShort(DOMElement& elem, const ChannelKey& key, const char* bName) {  
  const std::string tagName = bName == 0 ? Dom::getTagName(&elem) : bName;
  ConfigBranchImpl<UShort_t>* reg = static_cast<ConfigBranchImpl<UShort_t>*>(m_config->branch(tagName));
  UShort_t val(0);
  if ( reg == 0 or ! getUShort(elem,val) ) {
    return kFALSE;
  }
  if (key.hasBCAST()) {
    reg->setAll(val);
  } else {
    reg->setVal(key,val);
  }
  return kTRUE;
}

Bool_t ConfigReader::readUInt(DOMElement& elem, const ChannelKey& key, const char* bName ) {
  const std::string tagName =  bName == 0 ? Dom::getTagName(&elem) : bName;
  ConfigBranchImpl<UInt_t>* reg = static_cast<ConfigBranchImpl<UInt_t>*>(m_config->branch(tagName));
  UInt_t val(0);
  if ( reg == 0 or ! getUInt(elem,val) ) {
    return kFALSE;
  }
  if (key.hasBCAST()) {
    reg->setAll(val);
  } else {
    reg->setVal(key,val);
  }
  return kTRUE;
}

Bool_t ConfigReader::readULong(DOMElement& elem, const ChannelKey& key, const char* bName ) {
  const std::string tagName =  bName == 0 ? Dom::getTagName(&elem) : bName;
  ConfigBranchImpl<ULong64_t>* reg = static_cast<ConfigBranchImpl<ULong64_t>*>(m_config->branch(tagName));
  ULong64_t val(0);
  if ( reg == 0 or ! getULong(elem,val) ) {
    return kFALSE;
  }
  if (key.hasBCAST()) {
    reg->setAll(val);
  } else {
    reg->setVal(key,val);
  }
  return kTRUE;
}

Int_t ConfigReader::getIndex(DOMElement& elem, const std::string& rootName) {
  std::string fullName = Dom::getTagName(&elem);
  std::string endName(fullName,rootName.length()+1);
  char** nullPtr(0);
  return strtol(endName.c_str(),nullPtr,10);
}

Bool_t ConfigReader::getSptId(DOMElement& elem, Int_t& id) {
  id = ChannelKey::UNDEF;
  std::string ID("ID");
  std::string spt = Dom::getAttribute(&elem,ID);
  std::string BCAST("BCAST");
  if ( spt == BCAST ) { 
    id = ChannelKey::BCAST;
    return kTRUE;    
  }
  static std::map<std::string,int> sptMap;
  if ( sptMap.size() == 0 ) {
    sptMap["-x0"] = 0; sptMap["+x0"] = 9; sptMap["-y0"] = 18; sptMap["-y0"] = 27;
    sptMap["-x1"] = 1; sptMap["+x0"] = 10; sptMap["-y0"] = 19; sptMap["-y0"] = 28;
    sptMap["-x2"] = 2; sptMap["+x0"] = 11; sptMap["-y0"] = 20; sptMap["-y0"] = 29;
    sptMap["-x3"] = 3; sptMap["+x0"] = 12; sptMap["-y0"] = 21; sptMap["-y0"] = 30;
    sptMap["-x4"] = 4; sptMap["+x0"] = 13; sptMap["-y0"] = 22; sptMap["-y0"] = 31;
    sptMap["-x5"] = 5; sptMap["+x0"] = 14; sptMap["-y0"] = 23; sptMap["-y0"] = 32;
    sptMap["-x6"] = 6; sptMap["+x0"] = 15; sptMap["-y0"] = 24; sptMap["-y0"] = 33;
    sptMap["-x7"] = 7; sptMap["+x0"] = 16; sptMap["-y0"] = 25; sptMap["-y0"] = 34;
    sptMap["-x8"] = 8; sptMap["+x0"] = 17; sptMap["-y0"] = 26; sptMap["-y0"] = 35;
  }
  id = sptMap[spt]; 
  return kTRUE;
}
