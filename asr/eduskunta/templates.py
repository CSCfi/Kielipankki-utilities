# -*- coding: utf-8 -*-
# node template
node = """<?xml version="1.0" encoding="UTF-8"?>
<METATRANSCRIPT xmlns="http://www.mpi.nl/IMDI/Schema/IMDI" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Date="2017-06-08" FormatId="IMDI 3.03" Originator="Arbil.2.6.1109:" Type="CORPUS" Version="0" xsi:schemaLocation="http://www.mpi.nl/IMDI/Schema/IMDI ./IMDI_3.0.xsd">
  <Corpus>
    <Name>NAME-PH</Name>
    <Title>NAME-PH</Title>
    <Description LanguageId="" Link="">DESCRIPTION-PH</Description>
    <!--<CorpusLink Name=""></CorpusLink>-->
  </Corpus>
</METATRANSCRIPT>
"""

# session node template
sessionnode = """<?xml version="1.0" encoding="UTF-8"?>
<METATRANSCRIPT xmlns="http://www.mpi.nl/IMDI/Schema/IMDI"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                Date="2017-01-24"
                FormatId="IMDI 3.03"
                Originator="Arbil.2.6.1109:"
                Type="SESSION"
                Version="0"
                xsi:schemaLocation="http://www.mpi.nl/IMDI/Schema/IMDI ./IMDI_3.0.xsd">
  <Session>
      <Name>NAME-PH</Name>
      <Title>NAME-PH</Title>
      <Date>DATE-PH</Date>
      <Description LanguageId="" Link="">DESCRIPTION-PH</Description>
      <MDGroup>
         <Location>
            <Continent Link="http://www.mpi.nl/IMDI/Schema/Continents.xml" Type="ClosedVocabulary"/>
            <Country Link="http://www.mpi.nl/IMDI/Schema/Countries.xml" Type="OpenVocabulary">Finland</Country>
            <Region/>
            <Address/>
         </Location>
         <Project>
            <Name/>
            <Title/>
            <Id/>
            <Contact>
               <Name/>
               <Address/>
               <Email/>
               <Organisation/>
            </Contact>
            <Description LanguageId="" Link=""/>
         </Project>
         <Keys>
      </Keys>
         <Content>
            <Genre Link="http://www.mpi.nl/IMDI/Schema/Content-Genre.xml" Type="OpenVocabulary"/>
            <SubGenre Link="http://www.mpi.nl/IMDI/Schema/Content-SubGenre.xml" Type="OpenVocabularyList"/>
            <Task Link="http://www.mpi.nl/IMDI/Schema/Content-Task.xml" Type="OpenVocabulary"/>
            <Modalities Link="http://www.mpi.nl/IMDI/Schema/Content-Modalities.xml" Type="OpenVocabularyList"/>
            <Subject Link="http://www.mpi.nl/IMDI/Schema/Content-Subject.xml" Type="OpenVocabularyList"/>
            <CommunicationContext>
               <Interactivity Link="http://www.mpi.nl/IMDI/Schema/Content-Interactivity.xml" Type="ClosedVocabulary"/>
               <PlanningType Link="http://www.mpi.nl/IMDI/Schema/Content-PlanningType.xml" Type="ClosedVocabulary"/>
               <Involvement Link="http://www.mpi.nl/IMDI/Schema/Content-Involvement.xml" Type="ClosedVocabulary"/>
               <SocialContext Link="http://www.mpi.nl/IMDI/Schema/Content-SocialContext.xml" Type="ClosedVocabulary"/>
               <EventStructure Link="http://www.mpi.nl/IMDI/Schema/Content-EventStructure.xml" Type="ClosedVocabulary"/>
               <Channel Link="http://www.mpi.nl/IMDI/Schema/Content-Channel.xml" Type="ClosedVocabulary"/>
            </CommunicationContext>
            <Languages>
               <Description LanguageId="" Link=""/>
            </Languages>
            <Keys>
        </Keys>
            <Description LanguageId="" Link=""/>
         </Content>
         <Actors>
      </Actors>
      </MDGroup>
      <Resources>
         <MediaFile>
            <ResourceLink>VIDEO-PH</ResourceLink>
            <Type Link="http://www.mpi.nl/IMDI/Schema/MediaFile-Type.xml" Type="ClosedVocabulary">video</Type>
            <Format Link="http://www.mpi.nl/IMDI/Schema/MediaFile-Format.xml" Type="OpenVocabulary">video/mp4</Format>
            <Size/>
            <Quality Link="http://www.mpi.nl/IMDI/Schema/Quality.xml" Type="ClosedVocabulary">Unspecified</Quality>
            <RecordingConditions/>
            <TimePosition>
               <Start>Unspecified</Start>
               <End>Unspecified</End>
            </TimePosition>
            <Access>
               <Availability/>
               <Date/>
               <Owner/>
               <Publisher/>
               <Contact>
                  <Name/>
                  <Address/>
                  <Email/>
                  <Organisation/>
               </Contact>
               <Description LanguageId="" Link=""/>
            </Access>
            <Description LanguageId="" Link=""/>
            <Keys>
        </Keys>
         </MediaFile>
         
         <WrittenResource>
            <ResourceLink>ANNOTATION-PH</ResourceLink>
            <MediaResourceLink>ANNOTATION-PH</MediaResourceLink>
            <Date>Unspecified</Date>
            <Type Link="http://www.mpi.nl/IMDI/Schema/WrittenResource-Type.xml" Type="OpenVocabulary"/>
            <SubType Link="http://www.mpi.nl/IMDI/Schema/WrittenResource-SubType.xml" Type="OpenVocabularyList"/>
            <Format Link="http://www.mpi.nl/IMDI/Schema/WrittenResource-Format.xml" Type="OpenVocabulary">text/x-eaf+xml</Format>
            <Size/>
            <Validation>
               <Type Link="http://www.mpi.nl/IMDI/Schema/Validation-Type.xml" Type="ClosedVocabulary"/>
               <Methodology Link="http://www.mpi.nl/IMDI/Schema/Validation-Methodology.xml" Type="ClosedVocabulary"/>
               <Level>Unspecified</Level>
               <Description LanguageId="" Link=""/>
            </Validation>
            <Derivation Link="http://www.mpi.nl/IMDI/Schema/WrittenResource-Derivation.xml" Type="ClosedVocabulary">Unspecified</Derivation>
            <CharacterEncoding/>
            <ContentEncoding/>
            <LanguageId/>
            <Anonymized Link="http://www.mpi.nl/IMDI/Schema/Boolean.xml" Type="ClosedVocabulary">Unspecified</Anonymized>
            <Access>
               <Availability/>
               <Date>Unspecified</Date>
               <Owner/>
               <Publisher/>
               <Contact>
                  <Name/>
                  <Address/>
                  <Email/>
                  <Organisation/>
               </Contact>
               <Description LanguageId="" Link=""/>
            </Access>
            <Description LanguageId="" Link=""/>
            <Keys/>
         </WrittenResource>
      </Resources>
      <References>
    </References>
  </Session>
</METATRANSCRIPT>
"""


