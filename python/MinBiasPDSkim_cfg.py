import FWCore.ParameterSet.Config as cms

process = cms.Process("SKIM")

process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.2 $'),
    name = cms.untracked.string('$Source: /cvs_server/repositories/CMSSW/CMSSW/DPGAnalysis/Skims/python/MinBiasPDSkim_cfg.py,v $'),
    annotation = cms.untracked.string('Combined MinBias skim')
)

#
#
# This is for testing purposes.
#
#
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring('/store/data/BeamCommissioning09/MinimumBias/RECO/v2/000/123/151/6ADC6A1B-01DE-DE11-8FBD-00304879FA4A.root'),
                            secondaryFileNames = cms.untracked.vstring('/store/data/BeamCommissioning09/MinimumBias/RAW/v1/000/123/151/3CE3F1C6-FADD-DE11-8AEA-001D09F251D1.root')
)


process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(50)
)


#------------------------------------------
# Load standard sequences.
#------------------------------------------
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration/StandardSequences/GeometryIdeal_cff')


process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = 'GR09_P_V7::All' 

process.load("Configuration/StandardSequences/RawToDigi_Data_cff")
process.load("Configuration/StandardSequences/Reconstruction_cff")
process.load('Configuration/EventContent/EventContent_cff')

process.FEVTEventContent.outputCommands.append('drop *_MEtoEDMConverter_*_*')


######################################Reco Track#################################################

process.generalTracksFilter = cms.EDFilter("TrackCountFilter",
                                                      src = cms.InputTag('generalTracks'),
                                                      minNumber = cms.uint32(2) 
                                                      )
process.pixelLessTracksFilter = cms.EDFilter("TrackCountFilter",
                                                      src = cms.InputTag('ctfPixelLess'),
                                                      minNumber = cms.uint32(1) 
                                                      )
process.pixelTracksFilter = cms.EDFilter("TrackCountFilter",
                                                      src = cms.InputTag('pixelTracks'),
                                                      minNumber = cms.uint32(1) 
                                                      )

process.generalTracksPath = cms.Path(process.generalTracksFilter)
process.pixelTracksPath = cms.Path(process.pixelLessTracksFilter)
process.pixelLessTracksPath = cms.Path(process.pixelTracksFilter)


process.recotrackout = cms.OutputModule("PoolOutputModule",
                               outputCommands = process.FEVTEventContent.outputCommands,
                               SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('generalTracksPath',
    										'pixelTracksPath',
										'pixelLessTracksPath')),
                               dataset = cms.untracked.PSet(
			                 dataTier = cms.untracked.string('RAW-RECO'),
                                         filterName = cms.untracked.string('RecoTracks')),
                               fileName = cms.untracked.string('generalTracks.root')
                               )

###########################################################################################
#------------------------------------------
# parameters for the CSCSkim module
#------------------------------------------
process.load("DPGAnalysis/Skims/CSCSkim_cfi")


#set to minimum activity
process.cscSkim.minimumSegments = 1
process.cscSkim.minimumHitChambers = 1

# this is for filtering on HLT path
process.hltBeamHalo = cms.EDFilter("HLTHighLevel",
     TriggerResultsTag = cms.InputTag("TriggerResults","","HLT"),
     HLTPaths = cms.vstring('HLT_CSCBeamHalo','HLT_CSCBeamHaloOverlapRing1','HLT_CSCBeamHaloOverlapRing','HLT_CSCBeamHaloRing2or3'), # provide list of HLT paths (or patterns) you want
     eventSetupPathsKey = cms.string(''), # not empty => use read paths from AlCaRecoTriggerBitsRcd via this key
     andOr = cms.bool(True),             # how to deal with multiple triggers: True (OR) accept if ANY is true, False (AND) accept if ALL are true
     throw = cms.bool(False)    # throw exception on unknown path names
 )

#### the path
process.cscHaloSkim = cms.Path(process.hltBeamHalo+process.cscSkim)

process.options = cms.untracked.PSet(
 wantSummary = cms.untracked.bool(True)
)


#### output 
process.outputBeamHaloSkim = cms.OutputModule("PoolOutputModule",
    outputCommands = process.FEVTEventContent.outputCommands,
    fileName = cms.untracked.string("cscskimEvents.root"),
    dataset = cms.untracked.PSet(
      dataTier = cms.untracked.string('RAW-RECO'),
      filterName = cms.untracked.string('CSCSkim_BeamHalo')
    ),
    SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('cscHaloSkim'))
)

##################################################DT skim###############################################
process.muonDTDigis = cms.EDFilter("DTUnpackingModule",
    dataType = cms.string('DDU'),
    useStandardFEDid = cms.untracked.bool(True),
    fedbyType = cms.untracked.bool(True),
    readOutParameters = cms.PSet(
        debug = cms.untracked.bool(False),
        rosParameters = cms.PSet(
            writeSC = cms.untracked.bool(True),
            readingDDU = cms.untracked.bool(True),
            performDataIntegrityMonitor = cms.untracked.bool(False),
            readDDUIDfromDDU = cms.untracked.bool(True),
            debug = cms.untracked.bool(False),
            localDAQ = cms.untracked.bool(False)
        ),
        localDAQ = cms.untracked.bool(False),
        performDataIntegrityMonitor = cms.untracked.bool(False)
    )
)


process.hltDTActivityFilter = cms.EDFilter( "HLTDTActivityFilter",
 inputDCC         = cms.InputTag( "dttfDigis" ),   
 inputDDU         = cms.InputTag( "muonDTDigis" ),   
 inputDigis       = cms.InputTag( "muonDTDigis" ),   
 processDCC       = cms.bool( False ),   
 processDDU       = cms.bool( False ),   
 processDigis     = cms.bool( True ),   
 processingMode   = cms.int32( 0 ),   # 0=(DCC | DDU) | Digis/ 
                                      # 1=(DCC & DDU) | Digis/
                                      # 2=(DCC | DDU) & Digis/
                                      # 3=(DCC & DDU) & Digis/   
 minChamberLayers = cms.int32( 6 ),
 maxStation       = cms.int32( 3 ),
 minQual          = cms.int32( 2 ),   # 0-1=L 2-3=H 4=LL 5=HL 6=HH/
 minDDUBX         = cms.int32( 9 ),
 maxDDUBX         = cms.int32( 14 ),
 minActiveChambs  = cms.int32( 1 )
)


process.DTskim=cms.Path(process.muonDTDigis+process.hltDTActivityFilter)

process.DTskimout = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('DTSkim.root'),
    outputCommands = cms.untracked.vstring('keep *','drop *_MEtoEDMConverter_*_*'),
    dataset = cms.untracked.PSet(
    	      dataTier = cms.untracked.string('RAW-RECO'),
    	      filterName = cms.untracked.string('DT_skim')),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('DTskim','HLT_L1MuOpen:HLT','HLT_Activity_DT:HLT')
       )
)
####################################################################################

process.outpath = cms.EndPath(process.recotrackout+process.outputBeamHaloSkim+process.DTskimout)



 