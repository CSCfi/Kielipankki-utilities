<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

<!--  <xsl:output indent="no" method="xml"/>-->
  <xsl:output method="xml" indent="no"  encoding="UTF-8" omit-xml-declaration="yes"/>

  <xsl:variable name="reference" select="document('doria-nlfcl-pdflinks.xml')/doria_pdflinks"/>
  
  <xsl:template match="*">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="e-kirjat">
    <e-kirjat>
    <xsl:apply-templates>
      <xsl:sort select="metadata/author"/>
      <xsl:sort select="metadata/issued"/>
    </xsl:apply-templates>
    </e-kirjat>
  </xsl:template>
  
  <xsl:template match="KlK">
    <!--<xsl:call-template name="text"/>-->
    <xsl:variable name="work" select="work_id"/> 
    <xsl:element name="text">
      <xsl:attribute name="author">
	<xsl:choose>
	  <xsl:when test="author_fix">
	    <xsl:value-of select="author_fix"/>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="metadata/author"/>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="contributor"><xsl:value-of select="metadata/contributor"/></xsl:attribute>
      <xsl:attribute name="title"><xsl:value-of select="metadata/title"/></xsl:attribute>
      <xsl:attribute name="year"><xsl:value-of select="metadata/issued"/></xsl:attribute>
      <xsl:attribute name="lang"><xsl:value-of select="metadata/language"/></xsl:attribute>
      <xsl:attribute name="datefrom"><xsl:value-of select="metadata/issued"/></xsl:attribute>
      <xsl:attribute name="dateto"><xsl:value-of select="metadata/issued"/></xsl:attribute>
      <xsl:attribute name="timefrom"><xsl:value-of select="metadata/issued"/></xsl:attribute>
      <xsl:attribute name="timeto"><xsl:value-of select="metadata/issued"/></xsl:attribute>
      <xsl:attribute name="natlibfi"><xsl:value-of select="metadata/natlibfi"/></xsl:attribute>
      <xsl:attribute name="rights"><xsl:value-of select="metadata/rights"/></xsl:attribute>
      <xsl:attribute name="digitized"><xsl:value-of select="metadata/datestamp"/></xsl:attribute>
      <!--<xsl:attribute name="content_aggregator">Niklas Alén</xsl:attribute>-->
      <xsl:attribute name="filename">KlK_with_timestamps.xml</xsl:attribute>
      <xsl:attribute name="urn"><xsl:value-of select="urn"/></xsl:attribute>
      <!--<xsl:attribute name="pdf_url"><xsl:value-of select="pdf_url"/></xsl:attribute>-->
      <xsl:attribute name="pdflink">
	<xsl:text>|</xsl:text>
	<xsl:for-each select="$reference/work[@id=$work]/pdflink">
	  <xsl:value-of select="@url"/>
	  <xsl:text> </xsl:text>
	  <xsl:value-of select="@descr"/>
	  <xsl:text> (</xsl:text>
	  <xsl:value-of select="@size"/>
	  <xsl:text>)</xsl:text>
	  <xsl:text>|</xsl:text>
	</xsl:for-each>
      </xsl:attribute>
      <xsl:attribute name="html_url"><xsl:value-of select="html_url"/></xsl:attribute>
      <xsl:attribute name="publisher"><xsl:value-of select="publisher"/></xsl:attribute>
      <xsl:attribute name="license"><xsl:value-of select="license"/></xsl:attribute>
      <xsl:attribute name="pages"><xsl:value-of select="pages"/></xsl:attribute>
      <!--<xsl:attribute name="keywords"><xsl:value-of select="keywords"/></xsl:attribute>-->
      <xsl:attribute name="content_type"><xsl:value-of select="content_type"/></xsl:attribute>
      <xsl:attribute name="book_number"><xsl:value-of select="number"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

<!--  <xsl:template name="text">
    <xsl:element name="text">
    <xsl:attribute name="author"><xsl:value-of select="metadata/author"/></xsl:attribute>
    <xsl:attribute name="title"><xsl:value-of select="metadata/title"/></xsl:attribute>
    <xsl:attribute name="issued"><xsl:value-of select="metadata/issued"/></xsl:attribute>
    <xsl:attribute name="rights"><xsl:value-of select="metadata/rights"/></xsl:attribute>
    <xsl:attribute name="language"><xsl:value-of select="metadata/language"/></xsl:attribute>
    <xsl:attribute name="natlibfi"><xsl:value-of select="metadata/natlibfi"/></xsl:attribute>
    <xsl:attribute name="datestamp"><xsl:value-of select="metadata/datestamp"/></xsl:attribute>
    </xsl:element>
  </xsl:template>-->

  <xsl:template match="metadata"/>

  <xsl:template match="author_fix"/>

  <xsl:template match="number"/>

  <xsl:template match="urn"/>
  
  <xsl:template match="work_id"/>

  <xsl:template match="html_url"/>

  <xsl:template match="pages"/>

  <xsl:template match="publisher"/>

  <xsl:template match="license"/>

  <xsl:template match="keywords"/>

  <xsl:template match="content_type"/>

<!-- 22.8.2018 keep the page information -->
  <!--<xsl:template match="page">
    <xsl:apply-templates/>
  </xsl:template>-->
  
  

</xsl:stylesheet>
