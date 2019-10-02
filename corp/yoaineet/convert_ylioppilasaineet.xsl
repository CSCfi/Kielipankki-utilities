<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

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
  

  <xsl:template match="text">
    <xsl:element name="text">
      <xsl:attribute name="author"><xsl:value-of select="@candidate"/></xsl:attribute>
      <xsl:attribute name="author_name_type"><xsl:text>candidate id</xsl:text></xsl:attribute>
      <xsl:attribute name="author_sex"><xsl:value-of select="@candidate"/></xsl:attribute>
      <xsl:attribute name="filename"><xsl:value-of select="@file"/></xsl:attribute>
      <xsl:attribute name="grade_combined"><xsl:value-of select="@grade"/></xsl:attribute>
      <xsl:attribute name="grade_teacher"><xsl:value-of select="@grade"/></xsl:attribute>
      <xsl:attribute name="grade_censor"><xsl:value-of select="@grade"/></xsl:attribute>
      <xsl:attribute name="lang"><xsl:text>fin</xsl:text></xsl:attribute>
      <xsl:attribute name="topic_num_orig"><xsl:value-of select="@number"/></xsl:attribute>
      <xsl:attribute name="topic_num"><xsl:value-of select="@number"/></xsl:attribute>
      <xsl:attribute name="title"><xsl:value-of select="@heading"/></xsl:attribute>
      <xsl:attribute name="year"><xsl:value-of select="@year"/></xsl:attribute>

      <xsl:attribute name="datefrom"><xsl:value-of select="@year"/><xsl:text>0101</xsl:text></xsl:attribute>
      <xsl:attribute name="dateto"><xsl:value-of select="@year"/><xsl:text>1231</xsl:text></xsl:attribute>
      <xsl:attribute name="timefrom">000000</xsl:attribute>
      <xsl:attribute name="timeto">235959</xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>



 
</xsl:stylesheet>
