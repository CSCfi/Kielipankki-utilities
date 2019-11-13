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


  <xsl:template match="correction">
    <xsl:choose>
      <!--<xsl:when test="child::correction">
	<xsl:copy>
	  <xsl:for-each select="@*">
	    <xsl:copy/>
	  </xsl:for-each>
	  <xsl:attribute name="level">1</xsl:attribute>
	  <xsl:apply-templates/>
	</xsl:copy>
      </xsl:when>-->
      <xsl:when test="ancestor::correction">
	<xsl:copy>
	  <xsl:for-each select="@*">
	    <xsl:copy/>
	  </xsl:for-each>
	  <xsl:attribute name="level">2</xsl:attribute>
	  <xsl:apply-templates/>
	</xsl:copy>
      </xsl:when>
      <xsl:otherwise>
	<xsl:copy>
	  <xsl:for-each select="@*">
	    <xsl:copy/>
	  </xsl:for-each>
	  <xsl:attribute name="level">1</xsl:attribute>
	  <xsl:apply-templates/>
	</xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  
</xsl:stylesheet>
