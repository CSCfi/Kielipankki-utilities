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
     <!-- remove duplicate works -->
     <xsl:when test="(@book_number='841' or @book_number='850' or @book_number='302' or @book_number='273' or @book_number='931' or @book_number='955')"/>
     <xsl:when test="@lang='fin' or (@book_number='564' or @book_number='568' or @book_number='969' or @book_number='975' or @book_number='921' or @book_number='939')">
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
