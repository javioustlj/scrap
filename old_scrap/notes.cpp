FisuRxAxCBlock::FisuRxAxCBlock(u32 portNumber, u32 mapper)
    : FisuAxCBlock(portNumber, mapper)
    , mCrxDrv(std::move(AllResource::getCrxDriver(portNumber)))
    , m_blockIdDrv(std::move(AllResource::getDLDelayBlockId(portNumber)))
    , m_USblockIdDrv(std::move(AllResource::getUSBlockId(portNumber)))
    , m_Delay_block_id(INVALID_DLDELAY_BLOCKID)
    , m_us_blockId(INVALID_US_BLOCKID)
{
}



void FisuRxAxCBlock::Disable()
{
    bool isBBULink=false;
    m_enable = false;
    mCrxDrv->maskedWrite(FISU_CRX_AXC_GENERAL + mapper*FISU_CRX_AXC_LENGTH,
        SFisuCrxAxCGeneral::ENABLE::Set(0), SFisuCrxAxCGeneral::ENABLE::Mask());

    if (format == AxCConnectFormat::DLMULTICAST)
    {
	//bool isBBULink;
	u32 sourceLogicalLink = MAX_PORT_NUM;
	physical_2_logical_port(portNumber, isBBULink, sourceLogicalLink);

        u32 multicastBase = IQ_DL_MULTICAST_ENABLE + sourceLogicalLink * DL_SWITCH_REG_LENGTH;

	u32 axcBit=mapper;
	/*
	if (mapper >= 32)
	{
	  multicastBase += 4;
	  axcBit = mapper-32;
	} else {
	  axcBit = mapper;
	}
	*/

	mIqDrv->maskedWrite(multicastBase, 0<<axcBit,1<<axcBit);
    }

    u32 logicalLink=0;
    physical_2_logical_port(portNumber, isBBULink, logicalLink);
    if (isBBULink)
    {
        if ((m_Delay_block_id < INVALID_DLDELAY_BLOCKID) &&
            (m_blockIdDrv->key_return(m_Delay_block_id)))
        {
            mIqDrv->maskedWrite(IQ_DL_DELAY_ENABLE + DL_SWITCH_REG_LENGTH * logicalLink,
                            0, 1 << m_Delay_block_id);
            m_Delay_block_id = INVALID_DLDELAY_BLOCKID;
        }
    }

    if (mStreamId == INVALID_STREAMID)
    {
      return;
    }

  auto streamIt = mStreamPtr->find(mStreamId);
  if ( streamIt != mStreamPtr->end())
  {
    auto sourceIt= streamIt->second.m_source.begin();
    auto endIt= streamIt->second.m_source.end();
    u32 myAxcId = (portNumber << 8) | (mapper & 0xFF);
    while (sourceIt != endIt)
    {
      if (sourceIt->id == myAxcId)
      {
	sourceIt=streamIt->second.m_source.erase(sourceIt);
	break;
      }
      sourceIt ++;
    }

    if (!streamIt->second.m_target.empty())
    {
          AxcStatus source;
          source.protocol = PortProtocol::CPRI;
          source.id = (portNumber << 8) | (mapper & 0xFF);
          AxcStatus & target = streamIt->second.m_target.front();

	  if (format == AxCConnectFormat::NORMAL)
          {

	    connect(source, target, false);
            iqcompressionSampling(source, target, false);

	  } else if (format == AxCConnectFormat::SUMMING)
	  {
	      sum(source, target, streamIt->second.m_summingGroup, false);

	  } else {
	    dlmulticast(source, target, false);
	  }
    }

    if (streamIt->second.m_source.empty() && streamIt->second.m_target.empty())
    {
      if (streamIt->second.m_format == AxCConnectFormat::SUMMING)
      {
	mSumPtr->key_return(streamIt->second.m_summingGroup);
      }
      mStreamPtr->erase(streamIt);
    }
    return;
  }

    /*
      When FHS-radio link is broken, ObsaiOpticalBreakWisdom in Coco will delete all cofigured
      AxCs on this link. O&M also tries to delete these AxCs. Second delete will not find the
      AxCs becaused they are already deleted at the first time.
     */
    logger.info("FisuRxAxCBlock::disable: port %u AxC %u is not found. Maybe it is not configured or already deleted",
                portNumber, mapper);
}

void FisuRxAxCBlock::SetDLDelayThreshold(u32 dlayBuffThreshold)
{
  bool isBBULink=false;
  u32 logicalLink=0;
  //u32 m_blockID = ( portNumber << 8 ) | (mapper & 0xFF);
  physical_2_logical_port(portNumber, isBBULink, logicalLink);
  if (isBBULink && (dlayBuffThreshold > 0) && (dlayBuffThreshold < 0xFFF))
  {
      u32 dlDelay_block_id = INVALID_DLDELAY_BLOCKID;
      if ( (m_blockIdDrv->key_fetch(dlDelay_block_id)) &&
           (dlDelay_block_id < INVALID_DLDELAY_BLOCKID) )
      {
          m_Delay_block_id = dlDelay_block_id;
          u32 fieldSets =
              SFisuDLDelayAxC::AXC_ID::Set(mapper) |
              SFisuDLDelayAxC::DELAY_BLOCK_ID::Set(dlDelay_block_id)|
              SFisuDLDelayAxC::THRESHOLD::Set(dlayBuffThreshold);
          u32 fieldMask =
              SFisuDLDelayAxC::AXC_ID::Mask() |
              SFisuDLDelayAxC::DELAY_BLOCK_ID::Mask() |
              SFisuDLDelayAxC::THRESHOLD::Mask();

          mIqDrv->maskedWrite(IQ_DL_DELAY_AXC + DL_SWITCH_REG_LENGTH * logicalLink,
                              fieldSets, fieldMask);
          mIqDrv->maskedWrite(IQ_DL_DELAY_ENABLE + DL_SWITCH_REG_LENGTH * logicalLink,
                              1<<dlDelay_block_id, 1<<dlDelay_block_id);
      }
      else
      {
         std::string msg = "FisuRxAxCBlock::SetDLDelayThreshold"
         "All DL Delay block in use. "
         "(link:" + std::to_string(portNumber) + ")"+" Axc " + std::to_string(mapper) + "\n";
         throw FisuException(msg);
      }
  } // Not a BBU link. DL Delay can only be performed on BBU link
}

void FisuTxAxCBlock::Disable()
{
  m_enable = false;
  mCtxDrv->maskedWrite(FISU_CTX_AXC_GENERAL + mapper*FISU_CTX_AXC_LENGTH,
        SFisuCtxAxCGeneral::ENABLE::Set(0), SFisuCrxAxCGeneral::ENABLE::Mask());

  bool isBBULink=false;
  u32 logicalLink=0;
  physical_2_logical_port(portNumber, isBBULink, logicalLink);
  if (isBBULink)
  {
      if ((m_Delay_block_id < INVALID_ULDELAY_BLOCKID) &&
          (m_blockIdDrv->key_return(m_Delay_block_id)))
      {
           mIqDrv->maskedWrite(IQ_UL_DELAY_ENABLE + UL_SWITCH_REG_LENGTH * logicalLink,
                            0, 1 << m_Delay_block_id);
           m_Delay_block_id = INVALID_ULDELAY_BLOCKID;
      }
  }

  if (mStreamId == INVALID_STREAMID)
  {
    return;
  }

  auto streamIt = mStreamPtr->find(mStreamId);
  if ( streamIt != mStreamPtr->end())
  {
    auto targetIt= streamIt->second.m_target.begin();
    auto endIt= streamIt->second.m_target.end();
    u32 myAxcId = (portNumber << 8) | (mapper & 0xFF);
    while (targetIt != endIt)
    {
      if (targetIt->id == myAxcId)
      {
	targetIt=streamIt->second.m_target.erase(targetIt);
	break;
      }
      targetIt ++;
    }

    if (!streamIt->second.m_source.empty())
    {
          AxcStatus target = { };
          target.protocol = PortProtocol::CPRI;
          target.id = (portNumber << 8) | (mapper & 0xFF);
          AxcStatus & source = streamIt->second.m_source.front();

	  if (format == AxCConnectFormat::NORMAL)
          {
	    connect(source, target, false);
        iqcompressionSampling(source, target, false);

	  } else if (format == AxCConnectFormat::SUMMING)
	  {
	      sum(source, target, streamIt->second.m_summingGroup, false);

	  } else {
	    dlmulticast(source, target, false);

	  }
    }

  if (format == AxCConnectFormat::SUMMING)
  {
    u32 summinggroup = streamIt->second.m_summingGroup;

    u32 targetLogicalLink = MAX_PORT_NUM;
    physical_2_logical_port(portNumber, isBBULink, targetLogicalLink);

    u32 baseAddress = IQ_UL_INGR_AXC_ENABLE + targetLogicalLink*UL_SWITCH_REG_LENGTH + 12 * IQ_UL_INGR_AXC_LEN;

    mIqDrv->maskedWrite(baseAddress, 0, 1<<summinggroup);

    mIqDrv->maskedWrite(FISU_IQ_SUM_CTRL,0,1<<summinggroup);
  }

    if (streamIt->second.m_source.empty() && streamIt->second.m_target.empty())
    {
      if (streamIt->second.m_format == AxCConnectFormat::SUMMING)
      {
	      mSumPtr->key_return(streamIt->second.m_summingGroup);

      }
      mStreamPtr->erase(streamIt);
    }
    return;
  }

    /*
      When FHS-radio link is broken, ObsaiOpticalBreakWisdom in Coco will delete all cofigured
      AxCs on this link. O&M also tries to delete these AxCs. Second delete will not find the
      AxCs becaused they are already deleted at the first time.
     */
    logger.info("FisuTxAxCBlock::disable: port %u AxC %u is not found. Maybe it is not configured or already deleted.",
                portNumber, mapper);
}

void FisuTxAxCBlock::SetULDelayThreshold(u32 dlayBuffThreshold)
{
  bool isBBULink=false;
  u32 logicalLink=0;
  physical_2_logical_port(portNumber, isBBULink, logicalLink);
  if (isBBULink && (dlayBuffThreshold > 0) && (dlayBuffThreshold < 0xFFF))
  {
      u32 ulDelay_block_id = INVALID_ULDELAY_BLOCKID;
      if ( (m_blockIdDrv->key_fetch(ulDelay_block_id)) &&
           (ulDelay_block_id < INVALID_ULDELAY_BLOCKID) )
      {
          m_Delay_block_id = ulDelay_block_id;
          u32 fieldSets =
              SFisuULDelayAxC::AXC_ID::Set(mapper) |
              SFisuULDelayAxC::DELAY_BLOCK_ID::Set(ulDelay_block_id)|
              SFisuULDelayAxC::THRESHOLD::Set(dlayBuffThreshold);
          u32 fieldMask =
              SFisuULDelayAxC::AXC_ID::Mask() |
              SFisuULDelayAxC::DELAY_BLOCK_ID::Mask() |
              SFisuULDelayAxC::THRESHOLD::Mask();

          mIqDrv->maskedWrite(IQ_UL_DELAY_AXC + UL_SWITCH_REG_LENGTH * logicalLink,
                              fieldSets, fieldMask);
          mIqDrv->maskedWrite(IQ_UL_DELAY_ENABLE + UL_SWITCH_REG_LENGTH * logicalLink,
                              1<<ulDelay_block_id, 1<<ulDelay_block_id);
      }
      else
      {
         std::string msg = "FisuTxAxCBlock::SetULDelayThreshold"
         "All UL Delay block in use. "
         "(link:" + std::to_string(portNumber) + ")"+" Axc " + std::to_string(mapper) + "\n";
         throw FisuException(msg);
      }
  } // Not a BBU link. UL Delay can only be performed on BBU link
}

void FisuRxAxcPipeBlock::AxcRateEnable(bool enable)
{

  bool isBBULink=false;
  u32 logicalLink=0;
  u32 mapper = pipe / 3;
  u32 portNum = pipe/48;
  physical_2_logical_port(portNum,isBBULink, logicalLink);

  if (isBBULink)
  {
    u32 us_block_id = INVALID_US_BLOCKID;

    //enable up sampling.
    if(enable == true)
    {
      //associate the Axc with an available upsample block.
      if ( (m_blockIdDrv->key_fetch(us_block_id)) &&
	    (us_block_id < INVALID_US_BLOCKID))
     {
      u32 fieldSets =
        SFisuAxCUSRate::AXC_ID::Set(mapper) |
	SFisuAxCUSRate::US_BLOCK_ID::Set(us_block_id);
      u32 fieldMask =
        SFisuAxCUSRate::AXC_ID::Mask() |
        SFisuAxCUSRate::US_BLOCK_ID::Mask();

	//Establish connection between US block I and the Axc_ID
        mIqDrv->maskedWrite(IQ_DL_US_AXC + DL_SWITCH_REG_LENGTH * logicalLink,
				   fieldSets, fieldMask);

        mIqDrv->maskedWrite(IQ_DL_US_ENABLE + DL_SWITCH_REG_LENGTH * logicalLink,
			    1 << us_block_id, 1 << us_block_id);
	m_blockId = us_block_id;
      } //run out of US block resource.
      else
      {
         std::string msg = "FisuRxAxCPipeBlock::AxcRateEnable"
         "All UpSampling block in use. "
	 "(link:" + std::to_string(portNum) + ")"+" Axc " + std::to_string(mapper) + "\n";
         throw FisuException(msg);
      }
    }
    else //Disable up sampling for this AxC, if it has been enabled previously.
    {
      if ((m_blockId < INVALID_US_BLOCKID) &&
	  (m_blockIdDrv->key_return(m_blockId)))
      {
       mIqDrv->maskedWrite(IQ_DL_US_ENABLE + DL_SWITCH_REG_LENGTH * logicalLink,
			    0, 1 << m_blockId);
	m_blockId = INVALID_US_BLOCKID;
      }

    }
  }
  else
  {
         std::string msg = "FisuRxAxCPipeBlock::AxcRateEnable"
	 "Link:" + std::to_string(portNum) + "is not a BBU link.\n";
         throw FisuException(msg);
  }
}

void FisuTxAxcPipeBlock::AxcRateEnable(bool enable)
{

  bool isBBULink=false;
  u32 logicalLink=0;
  u32 mapper = pipe / 3; //AxC ID is related to the pipe id number.
  u32 portNum = pipe/48;
  physical_2_logical_port(portNum,isBBULink, logicalLink);

  if (isBBULink)
  {

    u32 ds_block_id = INVALID_DS_BLOCKID;
    //enable down sampling.
    if(enable == true)
    {
      //associate the Axc with an available downsample block.
      if ( (m_blockIdDrv->key_fetch(ds_block_id)) &&
	    (ds_block_id < INVALID_DS_BLOCKID))
      {
      u32 fieldSets =
           SFisuAxCDSRate::AXC_ID::Set(mapper) |
	   SFisuAxCDSRate::DS_BLOCK_ID::Set(ds_block_id);
      u32 fieldMask =
           SFisuAxCDSRate::AXC_ID::Mask() |
           SFisuAxCDSRate::DS_BLOCK_ID::Mask();


           mIqDrv->maskedWrite(IQ_UL_DS_AXC + UL_SWITCH_REG_LENGTH * logicalLink,
				   fieldSets, fieldMask);
           mIqDrv->maskedWrite(IQ_UL_DS_ENABLE + UL_SWITCH_REG_LENGTH * logicalLink,
			           1<<ds_block_id, 1<<ds_block_id);
	   m_blockId = ds_block_id;
      } //run out of DS block resource.
      else
      {
         std::string msg = "FisuTxAxCPipeBlock::AxcRateEnable"
         "All DownSampling block in use. "
	 "(link:" + std::to_string(portNum) + ")"+" Axc " + std::to_string(mapper) + "\n";
         throw FisuException(msg);
      }

    }
    else //Disable up sampling for this AxC, if it has been enabled previously. If the AxC ID has never been
      //up sample enabled, and the AxC ID is not found in the table, do nothing as by default no up sampling.
    {
      //Find the DownSample block ID used by this AxC, and
      //free this DS block to be available for other AxC to use.
      if ( (m_blockId < INVALID_DS_BLOCKID)  &&
	   (m_blockIdDrv->key_return(m_blockId)))
      {

        mIqDrv->maskedWrite(IQ_UL_DS_ENABLE + UL_SWITCH_REG_LENGTH * logicalLink,
			    0, 1 << m_blockId);
	m_blockId = INVALID_DS_BLOCKID;
      } // failure to find the block_id to disable. Assume it is never enabled
        // before and this is just a default action to disable UpSampling for this AxC.
    }
  }// Not a BBU link. Down Sampling can only be performed on BBU link
  else
  {

         std::string msg = "FisuTxAxCPipeBlock::AxcRateEnable"
	 "Link:" + std::to_string(portNum) + "is not a BBU link.\n";
         throw FisuException(msg);
  }
}
