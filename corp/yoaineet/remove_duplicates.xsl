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

 <xsl:template match="essays">
    <essay>
    <xsl:apply-templates/>
    </essay>
  </xsl:template>

 <xsl:template match="text">
   <xsl:choose>
     <!-- remove duplicate works -->
     <xsl:when test="@filename='2194.rtf' and @author='525 P'"/>
     <xsl:when test="not(@filename='102-247.rtf') and not(@filename='251-676.rtf') or (@filename='102-247.rtf' and (@author='207 T' or @author='217 T' or @author='227 T' or @author='231 T')) or (@filename='251-676.rtf' and (@author='347 T' or @author='551 P' or @author='615 T' or @author='625 T'))">
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
