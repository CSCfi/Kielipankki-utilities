<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

  <xsl:output method="xml" indent="no"  encoding="UTF-8" omit-xml-declaration="no"/>

  <xsl:variable name="reference" select="document('lonnrot-xml-showlink-map-20181029.xml')/references"/>


  <xsl:template match="*">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="letters/letter">
    <xsl:variable name="filename" select="@name"/>
    <xsl:element name="letter">
      <xsl:element name="show">
	<xsl:value-of select="$reference/ref[file=$filename]/address"/>
      </xsl:element>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
