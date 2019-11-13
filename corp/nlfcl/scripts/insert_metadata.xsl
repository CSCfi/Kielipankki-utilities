<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

<!--  <xsl:output indent="no" method="xml"/>-->
  <xsl:output method="xml" indent="no"  encoding="UTF-8" omit-xml-declaration="no"/>

  <xsl:variable name="doria_meta" select="document('doria-nlfcl-metadata-extract.xml')/doria_metadata"/>

  
  <xsl:template match="*">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>



  <xsl:template match="e-kirjat/KlK">
    <xsl:variable name="title" select="metadata/title"/>
    <xsl:variable name="author" select="metadata/author"/>
    <xsl:variable name="author_fix" select="author_fix"/>
    <xsl:variable name="issued" select="metadata/issued"/>
    <xsl:element name="KlK">
      <xsl:element name="urn">
	<xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@urn"/>
      </xsl:element>
      <xsl:element name="pdf_url">
        <xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@pdf_url"/>
      </xsl:element>
      <xsl:element name="html_url">
        <xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@html_url"/>
      </xsl:element>
      <xsl:element name="pages">
        <xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@pages"/>
      </xsl:element>
      <xsl:element name="publisher">
        <xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@publisher"/>
      </xsl:element>
      <xsl:element name="license">
	<xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@license"/>
      </xsl:element>
<!--      <xsl:element name="keywords">
        <xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author))]/meta/@keywords"/>
      </xsl:element>-->
      <xsl:element name="content_type">
        <xsl:value-of select="$doria_meta/work[meta/@title=$title and (meta/@author=$author or not(meta/@author) or meta/@author=$author_fix) and meta/@issued=$issued]/meta/@content_type"/>
      </xsl:element>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>
  



</xsl:stylesheet>
