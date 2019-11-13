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

  <xsl:template match="e-kirjat">
    <KlK>
    <xsl:apply-templates/>
    </KlK>
  </xsl:template>

  <xsl:template match="text">
    <xsl:choose>
      <xsl:when test="(@book_number='135' or @book_number='300' or @book_number='159' or @book_number='843' or @book_number='862')"/>
      <xsl:when test="@lang='swe' or (@book_number='476' or @book_number='585' or @book_number='822' or @book_number='845' or @book_number='853' or @book_number='863' or @book_number='931')">
	<xsl:copy>
	  <xsl:for-each select="@*">
            <xsl:copy/>
	  </xsl:for-each>
	  <xsl:apply-templates/>
	</xsl:copy>
      </xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>
  

</xsl:stylesheet>
