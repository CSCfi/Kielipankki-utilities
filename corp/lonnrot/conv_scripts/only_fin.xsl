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

<!-- <xsl:template match="e-kirjat">
    <KlK>
    <xsl:apply-templates/>
    </KlK>
  </xsl:template>
-->

 <xsl:template match="text">
   <xsl:choose>
     <xsl:when test="@lang='fin'">
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
