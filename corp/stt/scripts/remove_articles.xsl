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

 <xsl:template match="articles">
    <articles>
    <xsl:apply-templates/>
    </articles>
  </xsl:template>

 <xsl:template match="text">
   <xsl:choose>
     <!-- remove articles -->
     <xsl:when test="(@filename='94592711.xml' or @filename='5898333.xml' or @filename='5636473.xml' or @filename='5860244.xml' or @filename='5887905.xml' or @filename='102414155.xml' or @filename='97812776.xml' or @filename='100212577.xml' or @filename='102498667.xml')"/>
     <xsl:otherwise>
       <xsl:copy>
	 <xsl:for-each select="@*">
           <xsl:copy/>
	 </xsl:for-each>
	 <xsl:apply-templates/>
       </xsl:copy>
     </xsl:otherwise>
   </xsl:choose>
 </xsl:template>
 

</xsl:stylesheet>
