
#include "Config/ConfigTuple.h"

#include "TTree.h"
#include <iostream>

Int_t ConfigBranch::index(const ChannelKey& channel) const {
  Int_t idx = 0;
  if ( m_size.index3() > 1 ) { idx += channel.index3(); }
  if ( m_size.index2() > 1 ) { idx += (channel.index2() * m_size.index3()); }
  if ( m_size.index1() > 1 ) { idx += (channel.index1() * m_size.index2() * m_size.index3()); }
  if ( m_size.index0() > 1 ) { idx += (channel.index0() * m_size.index1() * m_size.index2() * m_size.index3()); }
  return idx;
}

void ConfigBranch::setLeafSuffix(std::string& leafName) const {
  char tmp[8];
  if ( m_size.index0() > 1 ) { sprintf(tmp,"[%i]",m_size.index0()); leafName += tmp; }
  if ( m_size.index1() > 1 ) { sprintf(tmp,"[%i]",m_size.index1()); leafName += tmp; }
  if ( m_size.index2() > 1 ) { sprintf(tmp,"[%i]",m_size.index2()); leafName += tmp; }
  if ( m_size.index3() > 1 ) { sprintf(tmp,"[%i]",m_size.index3()); leafName += tmp; }
  leafName += "/"; leafName += m_type;
}


template <typename T>
void ConfigBranchImpl<T>::setVal(const ChannelKey& key, T val) {
  Int_t i = index(key);
  m_vals[i] = val;
}

template <typename T>
void ConfigBranchImpl<T>::getVal(const ChannelKey& key, T& val) const {
  Int_t i = index(key);
  m_vals[i] = val;
}

template <typename T>
void ConfigBranchImpl<T>::setAll(T val) {
  Int_t idx = 0;
  for ( Int_t i(0); i < branchSize().index0(); i++ ) {    
    for ( Int_t j(0); j < branchSize().index1(); j++ ) {
      for ( Int_t k(0); k < branchSize().index2(); k++ ) {
	for ( Int_t l(0); l < branchSize().index3(); l++ ) {    
	  m_vals[idx] = val;
	  idx++;
	}    
      }    
    }
  }
}

template <typename T>
void ConfigBranchImpl<T>::attach(TTree& tree, const std::string& prefix) const {
  std::string branchName = prefix; branchName += name();
  std::string leafName = branchName;
  setLeafSuffix(leafName);
  tree.Branch(branchName.c_str(),(void*)(m_vals),leafName.c_str());
}


template <typename T>
void ConfigBranchImpl<T>::build() {
  Int_t bSize = branchSize().index0() * branchSize().index1() * branchSize().index2() * branchSize().index3();
  m_vals = new T[bSize];
}


ConfigBranchImpl<UShort_t> dummyShortBranch("",'s',ChannelKey());
ConfigBranchImpl<UInt_t> dummyIntBranch("",'i',ChannelKey());
ConfigBranchImpl<ULong64_t> dummyLongBranch("",'l',ChannelKey());


void ConfigTuple::reset() {  
  for ( std::list<ConfigBranch*>::iterator itr = m_branchList.begin();
	itr != m_branchList.end(); itr++ ) {
    (*itr)->reset();
  }
}

void ConfigTuple::attach(TTree& tree, const std::string& prefix) const {
  for ( std::list<ConfigBranch*>::const_iterator itr = m_branchList.begin();
	itr != m_branchList.end(); itr++ ) {
    (*itr)->attach(tree,prefix);
  }
}

void ConfigTuple::addBranch(ConfigBranch& aBranch) {
  std::map<std::string,ConfigBranch*>::iterator itrFind = m_branchMap.find(aBranch.name());
  if ( itrFind != m_branchMap.end() ) {
    std::cerr << "Branch " << aBranch.name() << " already exists" << std::endl;
    return;
  }
  m_branchMap[aBranch.name()] = &aBranch;
  m_branchList.push_back(&aBranch);
}

ConfigBranch* ConfigTuple::branch(const std::string& bname) {
  std::map<std::string,ConfigBranch*>::iterator itrFind = m_branchMap.find(bname);
  return itrFind != m_branchMap.end() ? itrFind->second: 0;
}
