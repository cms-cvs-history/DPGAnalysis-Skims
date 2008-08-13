import FWCore.ParameterSet.Config as cms

process = cms.Process("USER")

process.source = cms.Source("PoolSource",
       fileNames = cms.untracked.vstring (
       '/store/data/CRUZET3/EndcapsMuon/RAW/v4/000/051/285/0211AB52-4255-DD11-98AB-001617DC1F70.root',
       '/store/data/CRUZET3/EndcapsMuon/RAW/v4/000/051/285/749F97C6-FA54-DD11-8277-001617C3B710.root',
       '/store/data/CRUZET3/EndcapsMuon/RAW/v4/000/051/285/D25CA102-FE54-DD11-82FB-000423D6CA72.root'
      )
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)


#------------------------------------------
# Load standard sequences.
#------------------------------------------
process.load("Configuration/StandardSequences/Geometry_cff")
process.load("Configuration/StandardSequences/MagneticField_cff")
process.load("Configuration/StandardSequences/FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = 'CRZT210_V1::All' 
process.prefer("GlobalTag")
process.load("Configuration/StandardSequences/RawToDigi_Data_cff")
process.load("Configuration/StandardSequences/Reconstruction_cff")



#------------------------------------------
# parameters for the CSCSkim module
#------------------------------------------
##-- process.load("CSCSkim_cfi")
process.cscSkim = cms.EDFilter("CSCSkim",
    typeOfSkim         = cms.untracked.int32(1),
    rootFileName       = cms.untracked.string('outputDummy.root'),
    histogramFileName  = cms.untracked.string('histos.root'),
    nLayersWithHitsMinimum = cms.untracked.int32(3),
    minimumHitChambers = cms.untracked.int32(3),
    minimumSegments    = cms.untracked.int32(2),
    demandChambersBothSides = cms.untracked.bool(False),
    makeHistograms     = cms.untracked.bool(False)
)

#### the path

process.mySkim = cms.Path(process.muonCSCDigis*process.csc2DRecHits*process.cscSegments*process.cscSkim)


#### output 
process.outputSkim = cms.OutputModule("PoolOutputModule",
   fileName = cms.untracked.string("/tmp/schmittm/messyEvents.root"),
   SelectEvents = cms.untracked.PSet(
       SelectEvents = cms.vstring('mySkim')
       )
)

process.outpath = cms.EndPath(process.outputSkim)

#