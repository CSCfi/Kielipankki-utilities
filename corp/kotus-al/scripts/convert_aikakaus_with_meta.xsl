<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:kotus="http://www.kotus.fi/" xmlns:dcterms="http://purl.org/dc/terms/" version="2.0">

<!--  <xsl:output indent="no" method="xml"/>-->
  <xsl:output method="xml" indent="no"  encoding="UTF-8" omit-xml-declaration="yes"/>
  
  <xsl:template match="*">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>



  <xsl:template match="TEI.2">
    <xsl:element name="text">
      <xsl:variable name="meta" select="document(//sourceDesc/p)"/>
      <xsl:attribute name="corpus_name">The Magazine Corpus of the Institute for the Languages of Finland</xsl:attribute>
      <xsl:attribute name="corpus_shortname">kotus-al</xsl:attribute>
      <!--subcorpus has to be either perus or ydin; change by hand -->
      <xsl:attribute name="corpus_subcorpus">ydin</xsl:attribute>
      <!--subsubcorpus can be: ha, la, sk, su; change by hand -->
      <xsl:attribute name="corpus_id">kal_ydin_su</xsl:attribute>
      <xsl:attribute name="filename"><xsl:value-of select="$meta//rdf:Description/@rdf:about"/></xsl:attribute>
      <xsl:attribute name="metadata_filename"><xsl:value-of select="//sourceDesc/p"/></xsl:attribute>
      <!--The title of the magazine has to be changed by hand -->
      <xsl:attribute name="title">Suomi</xsl:attribute>
      <xsl:attribute name="description"><xsl:value-of select="$meta//rdf:Description/dc:description"/></xsl:attribute>
      <xsl:attribute name="year"><xsl:value-of select="$meta//rdf:Description/dc:coverage"/></xsl:attribute>
      <xsl:attribute name="issue"><xsl:value-of select="$meta//rdf:Description/@rdf:about"/></xsl:attribute>
      <xsl:attribute name="page"><xsl:value-of select="$meta//rdf:Description/@rdf:about"/></xsl:attribute>
      <xsl:attribute name="lang"><xsl:value-of select="$meta//rdf:Description/dc:language"/></xsl:attribute>
   <xsl:attribute name="contributor"><xsl:value-of select="$meta//rdf:Description/dc:contributor"/></xsl:attribute>
   <xsl:attribute name="publisher"><xsl:value-of select="$meta//rdf:Description/dc:publisher"/></xsl:attribute>
          <xsl:attribute name="datefrom"><xsl:value-of select="$meta//rdf:Description/dc:coverage"/></xsl:attribute>
      <xsl:attribute name="dateto"><xsl:value-of select="$meta//rdf:Description/dc:coverage"/></xsl:attribute>
      <xsl:attribute name="timefrom"><xsl:text>000000</xsl:text></xsl:attribute>
      <xsl:attribute name="timeto"><xsl:text>235959</xsl:text></xsl:attribute>
      <xsl:attribute name="year_digitized"><xsl:value-of select="$meta//rdf:Description/dc:date"/></xsl:attribute>
      <xsl:attribute name="date_modified"><xsl:value-of select="$meta//rdf:Description/dcterms:modified"/></xsl:attribute>
      <xsl:attribute name="wordcount"><xsl:value-of select="$meta//rdf:Description/dcterms:extent"/></xsl:attribute>
      
      <xsl:apply-templates/>
   </xsl:element>
  </xsl:template>



  <xsl:template match="teiHeader"/>

  

  <xsl:template match="body//*[not(self::p)]">
    <xsl:apply-templates/>
  </xsl:template>



  <!--<xsl:template match="p">
    <paragraph>
      <xsl:apply-templates/>
    </paragraph>
  </xsl:template>-->

  <xsl:template match="p">
    <xsl:element name="paragraph">
      <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
      <xsl:attribute name="rend"><xsl:value-of select="@rend"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>
  






</xsl:stylesheet>
